import sys
import types
import os
from . import atomic_integer
from .util import _log
from jennifer.agent import jennifer_agent

hooked_counter = atomic_integer.AtomicInteger()


def get_hooked_count():
    global hooked_counter
    return hooked_counter.value


class MethodSelector:

    ALL_PARAMETER = 0
    ARG_PARAMETER_ONLY = 1
    NAMED_PARAMETER_ONLY = 2
    BOTH_PARAMETER = 3
    RETURN_VALUE = 4

    UNDEFINED = 0
    MODULE_FUNCTION = 1
    CLASS_STATIC_METHOD = 2
    CLASS_INSTANCE_METHOD = 3

    def __init__(self, text, profile_return_value=False):
        self.text = text
        self.profile_module = None
        self.profile_class = None
        self.profile_func = None
        self.profile_arg_idx = []
        self.profile_arg_names = []
        self.is_initialized = False

        if profile_return_value:
            self.param_mode = MethodSelector.RETURN_VALUE
        else:
            self.param_mode = MethodSelector.ALL_PARAMETER

        self.is_instance = False
        self.original_target_container = None
        self.original_func = None
        self.func_type = MethodSelector.UNDEFINED

        try:
            self.parse_profile_item(text)
        except:
            _log('exception', 'invalid profile item', text)
            pass

    def parse_profile_item(self, item):
        item = str(item).strip()
        items = item.split(' ')
        if len(items) < 2:
            _log('warning', 'invalid profile item', item)
            return

        self.profile_module = items[0].strip()

        class_or_func = items[1].strip().split('.')
        if len(class_or_func) < 2:
            self.profile_func, arg_info = MethodSelector.parse_bracket(class_or_func[0].strip())
        else:
            self.profile_class = class_or_func[0].strip()
            if len(self.profile_class) == 0:
                self.profile_class = None
            self.profile_func, arg_info = MethodSelector.parse_bracket(class_or_func[1].strip())

        if len(items) >= 3:
            arg_text = MethodSelector.strip_curly_brace(''.join(items[2:]))
            arg_list = arg_text.split(',')
            for arg in arg_list:
                arg = arg.strip()

                try:
                    is_numeric_arg = arg.isnumeric()
                except AttributeError:
                    is_numeric_arg = unicode(arg).isnumeric()

                if arg_info is None:
                    if is_numeric_arg:
                        self.profile_arg_idx.append(int(arg))
                        self.param_mode |= MethodSelector.ARG_PARAMETER_ONLY
                    else:
                        self.profile_arg_names.append(arg)
                        self.param_mode |= MethodSelector.NAMED_PARAMETER_ONLY
                else:
                    if is_numeric_arg:
                        arg_pos = int(arg) - 1
                        if arg_pos >= len(arg_info):
                            arg_pos = arg
                        else:
                            arg_pos = arg_info[arg_pos]

                        if arg_pos.isnumeric():
                            self.profile_arg_idx.append(int(arg))
                            self.param_mode |= MethodSelector.ARG_PARAMETER_ONLY
                        else:
                            self.profile_arg_names.append(arg_pos)
                            self.param_mode |= MethodSelector.NAMED_PARAMETER_ONLY
                    else:
                        self.profile_arg_names.append(arg)
                        self.param_mode |= MethodSelector.NAMED_PARAMETER_ONLY

        self.is_initialized = True

    @staticmethod
    def parse_bracket(text):
        spos = text.find('(')
        if spos == -1:
            return text, None

        function_name = text[0:spos]
        epos = text.find(')Any')
        if epos == -1:
            return function_name, None

        arg_text = text[spos + 1:epos]
        if len(arg_text) == 0:
            return function_name, []

        arg_info = arg_text.split(',')
        return function_name, arg_info

    @staticmethod
    def strip_curly_brace(text):
        return text.strip().strip('{').strip('}')

    def process_dynamic_unhook(self):
        global hooked_counter

        if self.original_func is None:
            return

        if self.func_type == MethodSelector.MODULE_FUNCTION:
            if self.original_target_container is None:
                return

            self.original_target_container[self.profile_func] = self.original_func
            hooked_counter.dec()
        elif self.func_type == MethodSelector.CLASS_STATIC_METHOD:
            if self.original_target_container is None:
                return

            setattr(self.original_target_container, self.profile_func, staticmethod(self.original_func))
            hooked_counter.dec()
        elif self.func_type == MethodSelector.CLASS_INSTANCE_METHOD:
            if self.original_target_container is None:
                return

            setattr(self.original_target_container, self.profile_func, self.original_func)
            hooked_counter.dec()

    def process_dynamic_hook(self):
        import importlib

        try:
            module = importlib.import_module(self.profile_module)
        except Exception as e:
            _log('diagnostics', 'process_dynamic_hook', self.profile_module, 'not loaded')
            return

        target_func = None
        container_dict = None
        class_type = None
        if self.profile_class is not None:
            class_type = module.__dict__.get(self.profile_class, None)
            if class_type is not None:
                container_dict = class_type.__dict__
                target_func = class_type.__dict__.get(self.profile_func, None)
                if target_func is not None:
                    self.is_instance = isinstance(target_func, types.FunctionType)
        else:
            container_dict = module.__dict__
            target_func = module.__dict__.get(self.profile_func, None)

        if target_func is None:
            _log('diagnostics', 'process_dynamic_hook', self.profile_module, self.profile_func)
            return

        if self.hook_func(class_type, container_dict, target_func):
            global hooked_counter
            hooked_counter.inc()

    def hook_func(self, class_type, container_dict, target_func):
        self.original_target_container = container_dict
        target_func_text = str(target_func)

        if self.param_mode == MethodSelector.RETURN_VALUE:
            process_func = process_dynamic_return_user_id
        else:
            process_func = process_dynamic_param_user_id

        if self.is_instance:
            self.func_type = MethodSelector.CLASS_INSTANCE_METHOD
            if target_func_text.find('wrap_class_instance_method.<locals>.handler') != -1:
                return False

            setattr(class_type, self.profile_func, wrap_class_instance_method(target_func, process_func,
                                                                              self.param_mode,
                                                                              self.profile_arg_idx,
                                                                              self.profile_arg_names))

            self.original_target_container = class_type
            self.original_func = target_func

            _log('diagnostics', 'hook_func.instance_method', self.profile_module, self.profile_class,
                 self.profile_func, self.param_mode)
        else:
            if isinstance(target_func, staticmethod):
                self.func_type = MethodSelector.CLASS_STATIC_METHOD
                if target_func_text.find('wrap_class_static_method.<locals>.handler') != -1:
                    return False

                setattr(class_type, self.profile_func,
                        staticmethod(wrap_non_instance_method(target_func.__func__, process_func,
                                                              self.param_mode,
                                                              self.profile_arg_idx,
                                                              self.profile_arg_names)))

                self.original_target_container = class_type
                self.original_func = target_func.__func__

                _log('diagnostics', 'hook_func.static_method', self.profile_module, self.profile_class,
                     self.profile_func, self.param_mode)
            else:
                self.func_type = MethodSelector.MODULE_FUNCTION
                if target_func_text.find('wrap_global_function.<locals>.handler') != -1:
                    return False

                self.original_func = target_func
                container_dict[self.profile_func] = wrap_non_instance_method(target_func, process_func,
                                                                             self.param_mode,
                                                                             self.profile_arg_idx,
                                                                             self.profile_arg_names)

                _log('diagnostics', 'hook_func.module_func', self.profile_module, self.profile_class,
                     self.profile_func, self.param_mode)

        return True


def append_tuple_to_list(list_inst, tuple_inst, idx=None):
    if idx is None:
        list_inst.extend([str(item) for item in tuple_inst])
    else:
        for order, item in enumerate(tuple_inst):
            if (order + 1) in idx:
                list_inst.append(str(item))


def append_dict_to_list(list_inst, dict_inst, names=None):
    if names is None:
        list_inst.extend([str(value) for key, value in dict_inst.items()])
    else:
        for key, value in dict_inst.items():
            if key in names:
                list_inst.append(str(value))


def process_dynamic_return_user_id(args, kwargs, arg_result):
    try:
        agent = jennifer_agent()
        if agent is None:
            return

        o = agent.current_active_object()
        if o is None:
            return

        o.set_user_id(str(arg_result))
    except Exception as e:
        pass


def process_dynamic_param_user_id(param_mode, args, kwargs, arg_idx, arg_names):
    try:
        agent = jennifer_agent()
        user_id_list = []
        if agent is None:
            return

        o = agent.current_active_object()
        if o is None:
            return

        if param_mode == MethodSelector.ALL_PARAMETER:
            append_tuple_to_list(user_id_list, args)
            append_dict_to_list(user_id_list, kwargs)
        else:
            if param_mode | MethodSelector.ARG_PARAMETER_ONLY:
                append_tuple_to_list(user_id_list, args, idx=arg_idx)

            if param_mode | MethodSelector.NAMED_PARAMETER_ONLY:
                append_dict_to_list(user_id_list, kwargs, names=arg_names)

        o.set_user_id(''.join(user_id_list))
    except Exception as e:
        pass


def wrap_non_instance_method(org_func, target_func, param_mode, arg_idx, arg_names):

    def param_handler(*args, **kwargs):
        target_func(param_mode, args, kwargs, arg_idx, arg_names)
        return org_func(*args, **kwargs)

    def return_handler(*args, **kwargs):
        result = org_func(*args, **kwargs)
        target_func(args, kwargs, result)
        return result

    if param_mode == MethodSelector.RETURN_VALUE:
        return return_handler

    return param_handler


def wrap_class_instance_method(org_func, target_func, param_mode, arg_idx, arg_names):

    def param_handler(self, *args, **kwargs):
        target_func(param_mode, args, kwargs, arg_idx, arg_names)
        return org_func(self, *args, **kwargs)

    def return_handler(self, *args, **kwargs):
        result = org_func(self, *args, **kwargs)
        target_func(args, kwargs, result)
        return result

    if param_mode == MethodSelector.RETURN_VALUE:
        return return_handler

    return param_handler


class ClassSelector:

    def __init__(self, text_list, profile_return_value=False):
        self.method_list = []

        if text_list is None or len(text_list) == 0:
            return

        if isinstance(text_list, list) is False:
            return

        for text in text_list:
            parsed_item = MethodSelector(text, profile_return_value)
            if parsed_item is None:
                continue
            self.method_list.append(parsed_item)

    def process_hook(self):
        for method in self.method_list:
            try:
                method.process_dynamic_hook()
            except Exception as e:
                _log('exception', 'process_hook', method.text, e)

    def process_unhook(self):
        for method in self.method_list:
            try:
                method.process_dynamic_unhook()
            except Exception as e:
                _log('exception', 'process_unhook', method.text, e)


