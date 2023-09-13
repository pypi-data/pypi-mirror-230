from huhk.testcase.apache.data import data_list_str3, data_type, data_list_tuple

from huhk.unit_apache_beam import ApacheFun


class TestMap:
    # 带有预定义函数的 FlatMap
    def test_map_001(self):
        ApacheFun(data_list_str3, data_type=data_type).map(str.strip).print()

    # 带有lambda函数的Map
    def test_map_002(self):
        ApacheFun(data_list_str3, data_type=data_type).map(lambda x: x.strip('# \n')).print()

    def test_map_003(self):
        ApacheFun(data_list_tuple, data_type=data_type).map_tuple(lambda icon, plant: '{}{}'.format(icon, plant)).print()