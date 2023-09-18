# -*- coding: utf-8 -*-

import os
from jennifer.pconstants import *
import platform
from distutils.version import LooseVersion
from .util import _log

__current_python_ver__ = LooseVersion(platform.python_version())
__hooked_module__ = {}
python36_version = LooseVersion("3.6")

_original_builtins_open = None
_original_builtins_print = None
_original_builtins_socket_connect = None
_original_builtins_socket_connect_ex = None

from jennifer.agent import jennifer_agent

from . import app_flask
from . import db_sqlite3
from . import app_django
from . import db_mysqlclient
from . import db_pymysql
from . import external_requests
from . import external_urllib
from . import external_urllib2
from . import external_urllib3
from . import db_pymongo
from . import db_pymssql
from . import db_redis
from . import db_cx_oracle
from . import db_psycopg2
from . import db_pyodbc

HOOK_SUPPORT_LIST = [
    app_flask,
    app_django,
    db_mysqlclient,
    db_pymysql,
    db_sqlite3,
    db_pymongo,
    db_pymssql,
    db_psycopg2,
    db_cx_oracle,
    db_redis,
    db_pyodbc,
    external_urllib,
    external_urllib2,
    external_urllib3,
    external_requests,
]

if python36_version <= __current_python_ver__:
    try:
        from . import app_fastapi
        HOOK_SUPPORT_LIST.append(app_fastapi)
    except:
        pass

    try:
        from . import mod_asyncio
        HOOK_SUPPORT_LIST.append(mod_asyncio)
    except:
        pass


def _is_module_exist(module):
    try:
        return __import__(module)
    except ImportError:
        return False


def unhooking():
    global __hooked_module__

    if len(__hooked_module__) != 0:
        for mod_name in __hooked_module__.keys():
            hook_module = __hooked_module__[mod_name]['hook_module']
            target_module = __hooked_module__[mod_name]['target_module']

            try:
                if hook_module is not None and target_module is not None:
                    hook_module.unhook(target_module)
            except Exception as e:
                _log("exception", "unhooking", e)

    __hooked_module__ = {}
    _unhook_builtins()


def hooking():
    hooked_module = {}

    for m in HOOK_SUPPORT_LIST:
        try:
            module = _is_module_exist(m.__hooking_module__)

            if __current_python_ver__ < m.__minimum_python_version__:
                continue

            if module is not False:
                if m.hook(module) is True:
                    hooked_module[m.__hooking_module__] = {'target_module': module, 'hook_module': m,
                                                           'version': m.get_target_version()}
        except Exception as e:
            _log("exception", "hooking", e)

    global __hooked_module__
    __hooked_module__ = hooked_module
    _hook_builtins()


def _unhook_builtins():
    global _original_builtins_open
    global _original_builtins_print
    global _original_builtins_socket_connect
    global _original_builtins_socket_connect_ex

    try:
        import socket
        if _original_builtins_open is not None:
            __builtins__['open'] = _original_builtins_open

        if _original_builtins_print is not None:
            __builtins__['print'] = _original_builtins_print

        if _original_builtins_socket_connect is not None:
            socket.socket.connect = _original_builtins_socket_connect

        if _original_builtins_socket_connect_ex is not None:
            socket.socket.connect_ex = _original_builtins_socket_connect_ex
    except Exception as e:
        _log( "exception", "_hook_builtins", e)


# Socket Open/Connect 가로채기
def _hook_builtins():
    global _original_builtins_open
    global _original_builtins_print
    global _original_builtins_socket_connect
    global _original_builtins_socket_connect_ex

    try:
        import socket

        _original_builtins_open = __builtins__['open']
        __builtins__['open'] = _wrap_file_open(__builtins__['open'])

        if os.getenv('JENNIFER_PROFILE_PRINT'):
            _original_builtins_print = __builtins__['print']
            __builtins__['print'] = _wrap_file_print(__builtins__['print'])

        _original_builtins_socket_connect = socket.socket.connect
        socket.socket.connect = _wrap_socket_connect(socket.socket.connect)

        _original_builtins_socket_connect_ex = socket.socket.connect_ex
        socket.socket.connect_ex = _wrap_socket_connect(socket.socket.connect_ex)
    except Exception as e:
        _log("exception", "_hook_builtins", e)


def _wrap_file_print(origin_print):
    def _handler(*args, **kwargs):
        try:
            agent = jennifer_agent()
            if agent is not None:
                o = agent.current_active_object()

                if o is not None:
                    text = ' '.join(map(str, args))
                    o.profiler.add_message(text)
        except:
            pass

        return origin_print(*args, **kwargs)

    return _handler


def _wrap_file_open(origin_open):
    def _handler(file_path, mode='r', *args, **kwargs):
        try:
            agent = jennifer_agent()
            transaction = agent.current_active_object()

            if transaction is not None and 'site-packages' not in file_path:
                transaction.profiler.add_file_profile(
                    name=os.path.abspath(os.path.join(os.getcwd(), file_path)),
                    mode=mode
                )
        except:
            pass

        return origin_open(file_path, mode, *args, **kwargs)

    return _handler


def _wrap_socket_connect(origin_connect):
    import socket

    def _handler(self, address):
        agent = jennifer_agent()
        active_object = agent.current_active_object()

        try:
            ret = origin_connect(self, address)

            if self.family != socket.AF_INET:
                return ret

            if active_object is not None:
                remote_address = self.getpeername()
                local_address = self.getsockname()
                active_object.profiler.add_socket_profile(
                    host=remote_address[0],
                    port=remote_address[1],
                    local=local_address[1],
                )
            return ret
        except Exception as e:
            if active_object is not None:
                active_object.profiler.profile_exception_event(ERROR_TYPE_EXTERNAL_CALL_EXCEPTION, str(e))
            raise

    return _handler
