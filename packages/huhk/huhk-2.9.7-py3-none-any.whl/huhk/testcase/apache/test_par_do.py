import random

from huhk.testcase.apache.data import data_list_str2, data_type, data_list_dict

from huhk.unit_apache_beam import ApacheFun
from testcase.apache.beam_class import SplitWords, AnalyzeElement, DoFnMethods


class TestParDo:
    # 有简单 DoFn 的 ParDo
    def test_par_do_001(self):
        ApacheFun(data_list_str2, data_type=data_type).par_do(SplitWords(',')).print()

    # 带有时间戳和窗口信息的 ParDo
    def test_par_do_002(self):
        af = ApacheFun([':)'])
        af.map(lambda elem: af.window.TimestampedValue(elem, 1584675660))
        af.window_info(af.window.FixedWindows(30))
        af.par_do(AnalyzeElement()).print()

    # ParDo 与 DoFn 方法
    def test_par_do_003(self):
        ApacheFun(['🍓', '🥕', '🍆', '🍅', '🥔'], data_type=data_type).par_do(DoFnMethods()).print()

    # 使用函数进行分区
    def test_par_do_004(self):
        durations = ['annual', 'biennial', 'perennial']

        def by_duration(plant, num_partitions):
            return durations.index(plant['duration']) if plant['duration'] in durations else len(durations)

        out = ApacheFun(data_list_dict, data_type=data_type).partition(by_duration, 4)
        # out.print("'{}: {}'.format(x['duration'], x)")
        out.value[0].print("'annual: {}'.format(x)")
        out.value[1].print("'biennial: {}'.format(x)")
        out.value[2].print("'perennial: {}'.format(x)")
        out.create_or_update_project()

    # 使用 lambda 函数进行分区
    def test_par_do_005(self):
        durations = ['annual', 'biennial', 'perennial']
        out = ApacheFun(data_list_dict, data_type=data_type).partition(
            lambda plant, num_partitions:
            durations.index(plant['duration']) if plant['duration'] in durations else len(durations), 4)
        out.value[0].print("'annual: {}'.format(x)")
        out.value[1].print("'biennial: {}'.format(x)")
        out.value[2].print("'perennial: {}'.format(x)")
        out.create_or_update_project()

    # 具有多个参数的分区
    def test_par_do_006(self):

        def split_dataset(plant, num_partitions, ratio):
            assert num_partitions == len(ratio)
            bucket = random.randint(0, sum(ratio)-1)
            total = 0
            for i, part in enumerate(ratio):
                total += part
                if bucket < total:
                    return i
            return len(ratio) - 1

        out = ApacheFun(data_list_dict*3).partition(split_dataset, 2, ratio=[10, 20])
        out.value[0].print("'1: {}'.format(x)")
        out.value[1].print("'2: {}'.format(x)")
        out.create_or_update_project()
