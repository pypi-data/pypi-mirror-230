from huhk.testcase.apache.data import data_list_tuple, data_type

from huhk.unit_apache_beam import ApacheFun


class TestToString:
    # 字符串的元素
    def test_to_string_001(self):
        ApacheFun(data_list_tuple, data_type=data_type).to_string_kvs().print()

    # 字符串的元素
    def test_to_string_002(self):
        ApacheFun(data_list_tuple, data_type=data_type).to_string_element().print()

    # 字符串的元素
    def test_to_string_003(self):
        ApacheFun(data_list_tuple, data_type=data_type).to_string_iterables().print()