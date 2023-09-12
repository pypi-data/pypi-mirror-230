import unittest


def func_c(arg1, arg2):
    a_dict = {}
    # 其他代码
    return a_dict


def func_b(arg3, arg4):
    b_list = []
    a_arg1 = None
    a_arg2 = None
    # 其他代码
    a_dict = func_c(a_arg1, a_arg2)
    # 其他代码
    return b_list


def func_a():
    b_list = func_b('111', '222')
    if 'aaa' in b_list:
        return False
    return True


class FuncTest(unittest.TestCase):
    def test_func_a(self):
        assert func_a()