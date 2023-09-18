# -*- coding: utf-8 -*-
# import django.http
import traceback

from jennifer.wrap.wsgi import wrap_wsgi_app
from jennifer.agent import jennifer_agent
from jennifer.api.format import format_function
from distutils.version import LooseVersion

__hooking_module__ = 'django'
__minimum_python_version__ = LooseVersion("2.7")
__original_wsgi_handler_call = None
__original_wsgi_exception_handler_call = None
__target_version = None


def get_target_version():
    global __target_version
    return str(__target_version)


def unhook(django_module):
    if __original_wsgi_handler_call is not None:
        from django.core.handlers.wsgi import WSGIHandler
        WSGIHandler.__call__ = __original_wsgi_handler_call

    if __original_wsgi_exception_handler_call is not None:
        import django.core.handlers.exception
        django.core.handlers.exception.response_for_exception = __original_wsgi_exception_handler_call


def hook(django_module):
    from django.core.handlers.wsgi import WSGIHandler

    global __target_version
    __target_version = django_module.__version__

    def wrap_django_exception_handler(origin_wsgi_exception_func):
        def handler(*args, **kwargs):
            response = None

            try:
                exc = _safe_get(args, 1) or kwargs.get('exc') or None
                response = origin_wsgi_exception_func(*args, **kwargs)

                if response is not None and exc is not None:
                    response.current_exception_info = exc
            except:
                pass

            return response

        return handler

    def wrap_django_handler_class(origin_wsgi_entry_func):
        def handler(*args, **kwargs):
            origin_result = origin_wsgi_entry_func(*args, **kwargs)
            resolver = None

            try:
                if len(args) == 3:
                    self_wsgi = args[0]
                    self_environ = args[1]

                    request = self_wsgi.request_class(self_environ)  # origin_wsgi_entry_func보다 먼저 호출할 경우,
                                                                     # 한글이 포함된 NOT FOUND 경로를 요청하면,
                                                                     # origin_wsgi_entry_func에서 예외 발생

                    if hasattr(django_module, 'urls') and hasattr(django_module.urls, 'get_resolver'):
                        get_resolver = django_module.urls.get_resolver
                        if hasattr(request, 'urlconf'):
                            urlconf = request.urlconf
                            resolver = get_resolver(urlconf)
                        else:
                            resolver = get_resolver()
                    elif hasattr(django_module.core, 'urlresolvers'):
                        url_resolvers = django_module.core.urlresolvers
                        settings = django_module.conf.settings
                        urlconf = settings.ROOT_URLCONF
                        url_resolvers.set_urlconf(urlconf)
                        resolver = url_resolvers.RegexURLResolver(r'^/', urlconf)
                        if hasattr(request, 'urlconf'):
                            urlconf = request.urlconf
                            url_resolvers.set_urlconf(urlconf)
                            resolver = url_resolvers.RegexURLResolver(r'^/', urlconf)

                    if resolver is not None:
                        agent = jennifer_agent()
                        if agent is not None:
                            profiler = agent.current_active_object().profiler

                            if profiler is not None:
                                resolver_match = resolver.resolve(request.path_info)
                                name = format_function(resolver_match.func)

                                profiler.set_root_name(name)
            except:
                pass

            # origin_path_info: '/static/bbs/custom.css'
            # request.path: u'/static/bbs/custom.css'
            # request.get_full_path(): u'/static/bbs/custom.css'
            # request.build_absolute_uri(): 'http://localhost:18091/static/bbs/custom.css'

            return origin_result

        return handler

    global __original_wsgi_handler_call

    if str(WSGIHandler.__call__).startswith('jennifer.hooks') is True:
        return False

    __original_wsgi_handler_call = WSGIHandler.__call__   # 'django.core.handlers.wsgi.WSGIHandler.__call__'
    WSGIHandler.__call__ = wrap_django_handler_class(WSGIHandler.__call__)
    WSGIHandler.__call__ = wrap_wsgi_app(WSGIHandler.__call__)

    global __original_wsgi_exception_handler_call
    import django.core.handlers.exception
    __original_wsgi_exception_handler_call = django.core.handlers.exception.response_for_exception
    django.core.handlers.exception.response_for_exception \
        = wrap_django_exception_handler(django.core.handlers.exception.response_for_exception)

    return True


def _safe_get(properties, idx, default=None):
    try:
        return properties[idx]
    except IndexError:
        return default
