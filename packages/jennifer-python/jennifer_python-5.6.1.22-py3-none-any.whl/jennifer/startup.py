import os
import sys
from jennifer.agent import jennifer_agent
from .util import _log

# Not used
# def setup_log(config):
#     logger = logging.getLogger('jennifer')
#     logger.setLevel(logging.INFO)
#     logger.propagate = False
#     handler = logging.FileHandler(config['log_dir'])
#     formatter = logging.Formatter('%(asctime)s [JENNIFER Python] %(levelname)s %(message)s')
#     handler.setFormatter(formatter)
#     logger.addHandler(handler)
#     print('setup_log')

# config.address == /tmp/jennifer-...sock
# config.log_dir == /tmp


def _hook_uncaught_exception(exc_type, value, exc_tb):
    import traceback
    _log('exception', 'uncaught', exc_type, value, exc_tb)
    traceback.print_tb(exc_tb)


try:
    if os.getenv('JENNIFER_PY_DBG'):
        sys.excepthook = _hook_uncaught_exception
except:
    pass


def init():
    jennifer_agent()



