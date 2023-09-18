from distutils.version import LooseVersion
from .util import _log, _log_tb

__hooking_module__ = 'fastapi'
__minimum_python_version__ = LooseVersion("3.6")
_original_fastapi_module_fastapi = None
_original_fastapi_module_concurrency_run_in_threadpool = None
__target_version = None


def get_target_version():
    global __target_version
    return str(__target_version)


def _safe_get(properties, idx, default=None):
    try:
        return properties[idx]
    except IndexError:
        return default


def unhook(fastapi_module):
    if _original_fastapi_module_fastapi is not None:
        fastapi_module.FastAPI = _original_fastapi_module_fastapi

    if _original_fastapi_module_concurrency_run_in_threadpool is not None:
        fastapi_module.concurrency.run_in_threadpool = _original_fastapi_module_concurrency_run_in_threadpool


def hook(fastapi_module):
    global _original_fastapi_module_fastapi
    global _original_fastapi_module_concurrency_run_in_threadpool

    global __target_version
    __target_version = fastapi_module.__version__

    try:
        if str(fastapi_module.FastAPI).startswith('jennifer.hooks') is True:
            return False

        _original_fastapi_module_fastapi = fastapi_module.FastAPI
        _original_fastapi_module_concurrency_run_in_threadpool = fastapi_module.concurrency.run_in_threadpool

        fastapi_module.FastAPI = _wrap_fastapi(fastapi_module.FastAPI)
        fastapi_module.concurrency.run_in_threadpool = \
            _wrap_run_in_threadpool(fastapi_module.concurrency.run_in_threadpool)
    except Exception as e:
        _log('exception', __hooking_module__, 'hook', e)

    return True


def _wrap_fastapi(origin_fastapi):
    from jennifer.wrap import middleware_fastapi

    def _handler(*args, **kwargs):
        app = origin_fastapi(*args, **kwargs)
        app.add_middleware(middleware_fastapi.APMMiddleware)
        return app

    return _handler


def _wrap_run_in_threadpool(origin_run_in_threadpool):
    from jennifer.agent import jennifer_agent

    async def _handler(*args, **kwargs):
        active_object = None
        ctx_id = None
        pi_method = None

        try:
            agent = jennifer_agent()
            ctx_id = agent.get_ctx_id_func()
            func = _safe_get(args, 0) or kwargs.get('func') or None
            active_object = agent.current_active_object(ctx_id)

            if active_object is not None:
                pi_method = active_object.profiler.start_method("run_in_threadpool." + func.__name__)
        except:
            _log_tb('run_in_threadpool.pre')

        return_value = None
        err = None

        try:
            return_value = await origin_run_in_threadpool(*args, **kwargs)
        except Exception as e:
            err = e

        try:
            if pi_method is not None:
                active_object.profiler.end_method(pi_method, err)
        except:
            _log_tb('run_in_threadpool.post')

        if err is not None:
            raise err

        return return_value

    return _handler
