import os
from datetime import datetime
import traceback


def format_time(time_value):
    return time_value.strftime("%Y%m%d-%H%M%S")


def _log(level, *args):
    current_time = format_time(datetime.now())
    print(os.getpid(), current_time, '[jennifer]', level, args)


def _log_tb(*args):
    current_time = format_time(datetime.now())
    print(os.getpid(), current_time, '[jennifer]', 'exception', args)
    traceback.print_exc()
