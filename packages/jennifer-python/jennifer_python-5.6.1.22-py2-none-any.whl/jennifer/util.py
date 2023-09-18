import base64
import os
from datetime import datetime


def truncate_value(value, max_length):
    if len(value) > max_length:
        return value[:max_length] + '...'

    return value[:max_length]


def encode_base64_cookie(data):
    return base64.b64encode(data).decode('ascii').replace('=', '%3D')


def decode_base64_cookie(data):
    return base64.b64decode(data.replace('%3D', '='))


def process_url_additional_request_keys(dict_instance, req_uri, key_list, value_length):
    text = []

    for param_key in key_list:
        param_value = dict_instance.get(param_key)
        if param_value is None:
            continue

        if isinstance(param_value, list):
            text.append(param_key + '=' + truncate_value(','.join(param_value), value_length))
        elif isinstance(param_value, str):
            text.append(param_key + '=' + truncate_value(param_value, value_length))

    if len(text) == 0:
        return req_uri

    return req_uri + '+(' + '&'.join(text) + ')'


def profile_http_parameter_message(o, dict_instance, param_list, value_length):
    text = []

    for param_key in param_list:
        param_value = dict_instance.get(param_key)
        if param_value is None:
            continue

        if isinstance(param_value, list):
            text.append(param_key + '=' + truncate_value(','.join(param_value), value_length))
        elif isinstance(param_value, str):
            text.append(param_key + '=' + truncate_value(param_value, value_length))

    if len(text) != 0:
        o.profiler.add_message('HTTP-PARAM: ' + '; '.join(text))


def format_time(time_value):
    return time_value.strftime("%Y%m%d-%H%M%S")


def _log(level, *args):
    current_time = format_time(datetime.now())
    print(os.getpid(), current_time, '[jennifer]', level, args)
