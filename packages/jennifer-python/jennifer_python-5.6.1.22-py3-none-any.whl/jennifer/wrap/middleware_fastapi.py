import base64

from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar
import jennifer.agent.agent
import secrets
import time
import struct
import os
from email.utils import formatdate
import traceback
from jennifer.pconstants import *
import jennifer.util as util
from .util import _log, _log_tb

REQUEST_CTX_ID_KEY = "request_ctx_id"

wmonid_pack = struct.Struct('>Q')
_request_ctx_id = ContextVar(REQUEST_CTX_ID_KEY, default=None)


def get_request_ctx_id():
    ctx_value = _request_ctx_id.get()
    return ctx_value


# fastapi requires Python 3.6
class APMMiddleware(BaseHTTPMiddleware):

    @staticmethod
    def get_wmonid(request):
        wmon_id_value = None
        wmon_id_encoded = None

        cookie_wmonid = request.cookies.get('WMONID')
        if cookie_wmonid is not None:
            try:
                wmon_id_encoded = cookie_wmonid
                wmon_id_value, = wmonid_pack.unpack(util.decode_base64_cookie(wmon_id_encoded))
            except Exception as e:
                _log('exception', 'get_wmonid', cookie_wmonid, e)
                cookie_wmonid = None

        if wmon_id_value is None:
            wmon_id_value = (os.getpid() << 32) + int(time.time())
            wmon_id_encoded = wmonid_pack.pack(wmon_id_value)

        return wmon_id_value, wmon_id_encoded, cookie_wmonid is not None

    @staticmethod
    def set_wmonid(response, wmon_id_value, cookie_exists_wmonid, app_config):
        wmonid_cookie_expire_sec = 31536000
        wmonid_http_only = False
        wmonid_http_secure = False

        if app_config is not None:
            wmonid_cookie_expire_sec = app_config.expire_date_for_wmonid_cookie * 24 * 60 * 60
            wmonid_http_only = app_config.enable_http_only_for_wmonid_cookie
            wmonid_http_secure = app_config.enable_secure_for_wmonid_cookie

        if cookie_exists_wmonid:
            if wmonid_cookie_expire_sec < 0:
                response.set_cookie('WMONID', "deleted", expires='Thu, 01, Jan 1970 00:00:00 GMT', max_age=-1)
        else:
            expire = formatdate(timeval=time.time() + wmonid_cookie_expire_sec, localtime=False, usegmt=True)
            response.set_cookie('WMONID', util.encode_base64_cookie(wmon_id_value),
                                expires=expire, max_age=wmonid_cookie_expire_sec,
                                secure=wmonid_http_secure, httponly=wmonid_http_only)

    async def dispatch(self, request, call_next):
        active_object = None
        cookie_exists_wmonid = False
        wmonid_encoded = None
        agent_proxy = None
        profiler = None
        request_id = None
        response_key = None

        try:
            wmonid, wmonid_encoded, cookie_exists_wmonid = self.get_wmonid(request)

            agent_proxy = jennifer.agent.jennifer_agent()
            if agent_proxy is not None:
                agent_proxy.consume_apc_queue()
                jennifer.agent.agent.Agent.set_context_id_func(agent_proxy, get_request_ctx_id)
                request_id = _request_ctx_id.set(int.from_bytes(secrets.token_bytes(4), "big"))

                req_uri = request.url.path
                service_naming_http_header_key = agent_proxy.app_config.service_naming_by_http_header
                if service_naming_http_header_key is not None:
                    http_header_uri = request.headers.get(service_naming_http_header_key)
                    if http_header_uri is not None:
                        req_uri = "/" + http_header_uri

                method_value_length = agent_proxy.app_config.profile_method_return_value_length

                additional_url_keys = agent_proxy.app_config.url_additional_request_keys
                if additional_url_keys is not None and len(additional_url_keys) > 0:
                    req_uri = util.process_url_additional_request_keys(request.query_params, req_uri,
                                                                       additional_url_keys, method_value_length)

                active_object = agent_proxy.start_trace(request.headers, wmonid, req_uri)

                if active_object is not None:
                    if agent_proxy.app_config.enable_multi_tier_trace:
                        active_object.guid = request.headers.get(agent_proxy.app_config.guid_http_header_key)
                        if agent_proxy.app_config.topology_mode:
                            incoming_key = request.headers.get(agent_proxy.app_config.topology_http_header_key)
                            response_key = incoming_key
                            incoming_sid = request.headers.get(X_DOMAIN_ID)
                            incoming_agent_id = request.headers.get(X_AGENT_ID)
                            call_type_id = request.headers.get(X_CALLTYPE_ID)

                            active_object.set_incoming_info(call_type_id, incoming_key, incoming_sid, incoming_agent_id)

                    active_object.initialize("dispatch")
                    profiler = active_object.profiler
                    if agent_proxy.app_config.dump_http_query:
                        profiler.add_message('[%s] %s' % (request.method, str(request.url)))

                    header_value_length = agent_proxy.app_config.profile_http_value_length

                    if agent_proxy.app_config.profile_http_header_all:
                        active_object.profiler.add_message(
                            "HTTP-HEAD: " +
                            get_http_header_from_fastapi(request, header_value_length))
                    elif agent_proxy.app_config.profile_http_header is not None and\
                            len(agent_proxy.app_config.profile_http_header) != 0:
                        profile_http_header_message(active_object, request, agent_proxy.app_config.profile_http_header,
                                                    header_value_length)

                    param_list = agent_proxy.app_config.profile_http_parameter
                    if param_list is not None and len(param_list) > 0:
                        util.profile_http_parameter_message(active_object, request.query_params, param_list,
                                                            header_value_length)

        except:
            _log_tb('APMMiddleware.dispatch.pre')

        err = None
        response = None

        try:
            response = await call_next(request)

            if active_object is not None:
                active_object.http_status_code = response.status_code

                if response_key is not None:
                    response.headers[agent_proxy.app_config.topology_http_header_key] = str(response_key)
                    response.headers[X_DOMAIN_ID] = str(agent_proxy.domain_id)
                    response.headers[X_AGENT_ID] = str(agent_proxy.agent_id)

        except Exception as e:
            err = e

        if profiler is None:
            if request_id is not None:
                _request_ctx_id.reset(request_id)
            return response

        if err is not None:
            if hasattr(err, '__traceback__'):
                ex_result = traceback.format_exception(type(err), err, err.__traceback__)
                ex_result = ''.join(ex_result)
            else:
                ex_result = str(err)
            profiler.add_service_error_profile("Service Error: " + ex_result)

        try:
            if response is not None:
                if profiler is not None and response.status_code == 404:
                    profiler.add_service_error_profile(None)

                if agent_proxy is not None:
                    self.set_wmonid(response, wmonid_encoded, cookie_exists_wmonid, agent_proxy.app_config)

            if active_object is not None:
                agent_proxy.end_trace(active_object)
        except:
            _log_tb('APMMiddleware.dispatch.post')

        if request_id is not None:
            _request_ctx_id.reset(request_id)

        if err is not None:
            raise err

        return response


def profile_http_header_message(o, fastapi_req, header_list, header_max_length):
    text = []

    for header_key in header_list:
        header_value = fastapi_req.headers.get(header_key)
        if header_value is not None:
            text.append(header_key + '=' + util.truncate_value(header_value, header_max_length))

    if len(text) != 0:
        o.profiler.add_message('HTTP-HEAD: ' + '; '.join(text))


def get_http_header_from_fastapi(fastapi_req, header_max_length):
    text = []

    for header_key in fastapi_req.headers.keys():
        header_value = fastapi_req.headers.get(header_key)
        if header_value is not None:
            text.append(header_key + '=' + util.truncate_value(header_value, header_max_length))

    return '; '.join(text)
