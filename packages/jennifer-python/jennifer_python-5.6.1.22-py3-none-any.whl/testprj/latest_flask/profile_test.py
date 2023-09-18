import os


g_user_id = None
g_user_name = None


def get_my_id():
    global g_user_id

    if g_user_id is None:
        return str(os.getpid())

    return g_user_id


def set_my_id(value):
    global g_user_id
    g_user_id = value


def set_my_id_name(value, name='test'):
    global g_user_id, g_user_name
    g_user_id = value
    g_user_name = name


def set_my_id_name_test_2(value, name='test', age=50):
    global g_user_id, g_user_name
    g_user_id = value
    g_user_name = name


class MyTest:
    def __init__(self):
        self.name = 'test'
        self.age = 50

    def get_name(self, idx, my_arg=',test'):
        return self.name

    def set_my_name(self, name):
        self.name = name

    @staticmethod
    def set_id(text):
        return str(text).lower()

    def get_age(self):
        return self.age
