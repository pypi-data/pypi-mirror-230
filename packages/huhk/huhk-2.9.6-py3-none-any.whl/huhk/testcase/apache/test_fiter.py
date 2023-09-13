from huhk.unit_apache_beam import ApacheFun


class TestFiter:
    def setup(self):
        self.af = ApacheFun(data_list_dict, data_type=data_type)

    # 使用函数过滤
    def test_fiter_001(self):
        def is_perennial(plant):
            return plant['duration'] == 'perennial'
        self.af.filter(is_perennial).print()

    # 使用 lambda 函数过滤
    def test_fiter_002(self):
        self.af.filter(lambda plant: plant['duration'] == 'perennial').print()

    # 使用多个参数进行过滤
    def test_fiter_003(self):
        def has_duration(plant, duration):
            return plant['duration'] == duration
        self.af.filter(has_duration, 'annual').print()

    # 将输入作为单例进行过滤
    def test_fiter_004(self):
        self.af.filter(lambda plant, duration: plant['duration'] == duration,
                       duration=self.af.pvalue_as_singleton(['perennial'])).print()

    # 将输入作为迭代器进行过滤
    def test_fiter_005(self):
        self.af.filter(lambda plant, duration: plant['duration'] in duration,
                       duration=self.af.pvalue_as_iter(['annual', 'perennial'])).print()

    # 将输入作为字典进行过滤
    def test_fiter_006(self):
        data = [('annual', False), ('biennial', False), ('perennial', True)]
        self.af.filter(lambda plant, duration: duration.get(plant['duration']),
                       duration=self.af.pvalue_as_dict(data)).print()
