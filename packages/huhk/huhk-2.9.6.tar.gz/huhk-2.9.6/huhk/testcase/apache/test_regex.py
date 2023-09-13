from huhk.testcase.apache.data import data_list_str4, data_type, data_list_str5

from huhk.unit_apache_beam import ApacheFun


class TestRegex:
    # 正则表达式匹配
    def test_regex_001(self):
        ApacheFun(data_list_str4, data_type=data_type).regex_matches(r'(?P<icon>[^\s,]+), *(\w+), *(\w+)').print()

    # 正则表达式与所有组匹配
    def test_regex_002(self):
        ApacheFun(data_list_str4, data_type=data_type).regex_all_match(r'(?P<icon>[^\s,]+), *(\w+), *(\w+)').print()

    # 正则表达式匹配成键值对
    def test_regex_003(self):
        ApacheFun(data_list_str4, data_type=data_type).regex_matches_kv(r'(?P<icon>[^\s,]+), *(\w+), *(\w+)', 'icon').print()

    # 正则表达式查找
    def test_regex_004(self):
        ApacheFun(data_list_str4, data_type=data_type).regex_find(r'(?P<icon>[^\s,]+), *(\w+), *(\w+)').print()

    # 正则表达式查找所有
    def test_regex_005(self):
        ApacheFun(data_list_str5, data_type=data_type).regex_find_all(r'(?P<icon>[^\s,]+), *(\w+), *(\w+)').print()

    # 正则表达式查找为键值对
    def test_regex_006(self):
        ApacheFun(data_list_str5).regex_find_kv(r'(?P<icon>[^\s,]+), *(\w+), *(\w+)', 'icon').print()

    # 正则表达式替换
    def test_regex_007(self):
        ApacheFun(data_list_str5, data_type=data_type).regex_replace_all(r'\s*,\s*', ':').print()

    # 先替换正则表达式
    def test_regex_008(self):
        ApacheFun(data_list_str5, data_type=data_type).regex_replace_first(r'\s*,\s*', ': ').print()

    # 正则表达式拆分
    def test_regex_009(self):
        ApacheFun(data_list_str5, data_type=data_type).regex_split(r'\s*,\s*').print()
