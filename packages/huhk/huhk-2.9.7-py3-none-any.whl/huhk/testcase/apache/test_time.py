from huhk.testcase.apache.data import data_list_dict3, data_type

from huhk.unit_apache_beam import ApacheFun


class TestTimes:
    # 按事件时间标记时间戳
    def test_times_001(self):
        ApacheFun(data_list_dict3, data_type=data_type).timestamped_value("season").print()

    def test_times_002(self):
        ApacheFun(data_list_dict3, data_type=data_type).timestamped_value("season2").print()

    def test_times_003(self):
        ApacheFun(data_list_dict3, data_type=data_type).timestamped_value().print()

    def test_times_004(self):
        ApacheFun(data_list_dict3, data_type=data_type).timestamped_value("season", type="utc").print()

    def test_times_005(self):
        ApacheFun(data_list_dict3, data_type=data_type).timestamped_value("season", type="bj").print()

    def test_times_006(self):
        ApacheFun(data_list_dict3, data_type=data_type).timestamped_value("season", type="rfc").print()

    def test_times_007(self):
        ApacheFun(data_list_dict3, data_type=data_type).timestamped_value("season", type="proto").print()

    def test_times_008(self):
        ApacheFun(data_list_dict3, data_type=data_type).timestamped_value("season", type="s").print()

    def test_times_009(self):
        ApacheFun(data_list_dict3, data_type=data_type).timestamped_value("season", type="m").print()

    def test_times_010(self):
        ApacheFun(data_list_dict3, data_type=data_type).timestamped_value("season", type="h").print()

    def test_times_011(self):
        ApacheFun(data_list_dict3, data_type=data_type).timestamped_value("season", type="t").print()
