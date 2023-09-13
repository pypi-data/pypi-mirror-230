from huhk.testcase.apache.data import data_list_str, data_type, data_list_str2, data_list_list, data_list_tuple, \
    data_list_dict, data_list_dict2

from huhk.unit_apache_beam import ApacheFun


class TestFlatmap:
    def setup(self):
        self.af = ApacheFun(data_list_str, data_type=data_type)

    # 带有预定义函数的 FlatMap
    def test_flatmap_001(self):
        self.af.flat_map(str.split).print()

    # 带有函数的FlatMap
    def test_flatmap_002(self):
        self.af.set_data(data_list_str2)
        self.af.flat_map(lambda x: x.split(",")).print()

    # 带有生成器的FlatMap
    def test_flatmap_003(self):
        def generate_elements(elements):
            for element in elements:
                yield element
        self.af.set_data(data_list_list)
        self.af.flat_map(generate_elements).print()

    # 键值对的FlatMapTuple
    def test_flatmap_004(self):
        def format_plant(icon, plant):
            if icon:
                yield '{}{}'.format(icon, plant)
        self.af.set_data(data_list_tuple)
        self.af.flat_map_tuple(format_plant).print()

    # 带有多个参数的 FlatMap
    def test_flatmap_005(self):
        def split_words(text, delimiter=None):
            return text.split(delimiter)
        self.af.set_data(data_list_str2)
        self.af.flat_map(split_words, ",").print()

    # 将输入作为迭代器的 FlatMap
    def test_flatmap_006(self):
        def normalize_and_validate_durations(plant, valid_durations):
            plant['duration'] = plant['duration'].lower()
            if plant['duration'] in valid_durations:
                yield plant
        self.af.set_data(data_list_dict)
        self.af.flat_map(normalize_and_validate_durations, self.af.pvalue_as_iter(data_list)).print()

    # 将输入作为字典的 FlatMap
    def test_flatmap_007(self):
        def replace_duration_if_valid(plant, durations):
            if plant['duration'] in durations:
                plant['duration'] = durations[plant['duration']]
                yield plant
        self.af.set_data(data_list_dict2)
        self.af.flat_map(replace_duration_if_valid, self.af.pvalue_as_dict(data_list_tuple2)).print()