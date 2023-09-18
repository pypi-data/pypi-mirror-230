from distutils.version import LooseVersion
from jennifer.pconstants import *

__hooking_module__ = 'pymysql'
__minimum_python_version__ = LooseVersion("2.7")
_original_db_connect = None
__target_version = None


def get_target_version():
    global __target_version
    return str(__target_version)


def safe_get(properties, idx, default=None):
    try:
        return properties[idx]
    except IndexError:
        return default


def connection_info(*args, **kwargs):
    host = safe_get(args, 0) or kwargs.get('host')
    port = safe_get(args, 4) or kwargs.get('port') or 3306
    database = safe_get(args, 3) or kwargs.get('database') or kwargs.get('db')
    return host, port, database, None


def unhook(pymysql_module):
    global _original_db_connect
    if _original_db_connect is not None:
        pymysql_module.connect = _original_db_connect


def hook(pymysql_module):
    from jennifer.wrap import db_api

    global __target_version
    __target_version = pymysql_module.version_info

    global _original_db_connect
    if str(pymysql_module.connect).startswith('jennifer.hooks') is True:
        return False

    _original_db_connect = db_api.register_database(pymysql_module, REMOTE_CALL_TYPE_MYSQL, connection_info)
    return True
