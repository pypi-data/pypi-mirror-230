from huhk.testcase.apache.data import data_type, data_list_tuple3, data_list_tuple4, data_list_tuple5, data_list2, \
    data_list_set, data_list_tuple_list, data_list_tuple_list2, data_list, data_list_group, data_list_dict3, \
    data_list_tuple_dict, data_list3

from testcase.apache.beam_class import AverageFn, AverageFn2
from huhk.unit_apache_beam import ApacheFun


class TestPolymerization:
    # 通过键聚合所有输入元素，并允许下游处理使用与键关联的所有值
    def test_polymerization_001(self):
        ApacheFun(data_type=data_type).co_group_by_key(icons=data_list_tuple3, durations=data_list_tuple4).print()

    def test_polymerization_002(self):
        ApacheFun(data_type=data_type).co_group_by_key(data_list_tuple3, data_list_tuple4, data_list_tuple4).print()

    # 组合集合中的所有元素
    def test_polymerization_003(self):
        def get_common_items(sets):
            return set.intersection(*(sets or [set()]))
        ApacheFun(data_list_set, data_type=data_type).combine_globally(get_common_items).print()

    def test_polymerization_004(self):
        ApacheFun(data_list_set, data_type=data_type).combine_globally(lambda sets: set.intersection(*(sets or [set()]))).print()

    def test_polymerization_005(self):
        ApacheFun(data_list_set, data_type=data_type).combine_globally(
            lambda sets, exclude: set.intersection(*(sets or [set()])) - exclude, exclude={'🥕'}).print()

    def test_polymerization_006(self):
        ApacheFun(data_list2, data_type=data_type).combine_percentages_fn(type=3).print()

    # 组合集合中每个键的所有元素
    def test_combine_per_key_007(self):
        ApacheFun(data_list_tuple5, data_type=data_type).combine_per_key(sum).print()

    def test_combine_per_key_008(self):
        def saturated_sum(values):
            max_value = 8
            return min(sum(values), max_value)
        ApacheFun(data_list_tuple5, data_type=data_type).combine_per_key(saturated_sum).print()

    def test_combine_per_key_009(self):
        ApacheFun(data_list_tuple5, data_type=data_type).combine_per_key(lambda values: min(sum(values), 8)).print()

    def test_combine_per_key_010(self):
        ApacheFun(data_list_tuple5, data_type=data_type).combine_per_key(
            lambda values, max_value: min(sum(values), max_value), max_value=8).print()

    def test_combine_per_key_011(self):
        ApacheFun(data_list_tuple5, data_type=data_type).combine_per_key(AverageFn()).print()

    # 在键控元素集合中组合可迭代的值
    def test_combine_values_012(self):
        ApacheFun(data_list_tuple_list, data_type=data_type).combine_values(sum).print()

    def test_combine_values_013(self):
        def saturated_sum(values):
            max_value = 8
            return min(sum(values), max_value)
        ApacheFun(data_list_tuple_list, data_type=data_type).combine_values(saturated_sum).print()

    def test_combine_values_014(self):
        ApacheFun(data_list_tuple_list, data_type=data_type).combine_values(lambda values: min(sum(values), 8)).print()

    def test_combine_values_015(self):
        ApacheFun(data_list_tuple_list, data_type=data_type).combine_values(
            lambda values, max_value: min(sum(values), max_value), max_value=8).print()

    def test_combine_values_016(self):
        ApacheFun(data_list_tuple_list2, data_type=data_type).combine_values(AverageFn2()).print()

    # 计算每个聚合中的元素个数
    def test_count_017(self):
        ApacheFun(data_list2, data_type=data_type).count_globally().print()

    def test_count_018(self):
        ApacheFun(data_list_tuple5, data_type=data_type).count_per_key().print()

    def test_count_019(self):
        ApacheFun(data_list2, data_type=data_type).count_per_element().print()

    # 生成一个包含输入集合的不同元素的集合
    def test_distinct_020(self):
        ApacheFun(data_list2, data_type=data_type).distinct().print()

    def test_group_by_key_021(self):
        ApacheFun(data_list_tuple5, data_type=data_type).group_by_key().print()

    def test_group_by_022(self):
        ApacheFun(data_list2, data_type=data_type).group_by(lambda s: s[0]).print()

    def test_group_by_023(self):
        ApacheFun(data_list, data_type=data_type).group_by(letter=lambda s: s[0], is_berry=lambda s: 'bie' in s).print()

    def test_group_by_024(self):
        ApacheFun(data_list_group, data_type=data_type).group_by('recipe').print()

    def test_group_by_025(self):
        ApacheFun(data_list_group, data_type=data_type).group_by("recipe", is_berry=lambda x: 'berry' in x.fruit).print()

    def test_group_by_026(self):
        ApacheFun(data_list_group, data_type=data_type).group_by("recipe")\
            .aggregate_field('quantity', sum, 'total_quantity').print()

    def test_group_by_027(self):
        af = ApacheFun(data_list_group, data_type=data_type)
        af.group_by()
        af.aggregate_field('quantity', sum, 'total_quantity')
        af.aggregate_field(lambda x: x.quantity * x.unit_price, sum, 'price')
        af.print()

    def test_group_into_batches_028(self):
        ApacheFun(data_list_tuple5, data_type=data_type).group_into_batches(2).print()

    def test_latest_globally_029(self):
        af = ApacheFun(data_list_dict3)
        af.latest_globally("season")
        af.print()

    def test_latest_per_key_030(self):
        af = ApacheFun(data_list_tuple_dict)
        af.latest_per_key("harvest", "item")
        af.print()

    def test_max_031(self):
        ApacheFun(data_list3, data_type=data_type).max().print()

    def test_max_032(self):
        ApacheFun(data_list_tuple5, data_type=data_type).max().print()

    def test_min_033(self):
        ApacheFun(data_list3, data_type=data_type).min().print()

    def test_min_034(self):
        ApacheFun(data_list_tuple5, data_type=data_type).min().print()

    def test_mean_035(self):
        """入：[3, 4, 1, 2]
           出：2.5"""
        ApacheFun(data_list3, data_type=data_type).mean().print()

    def test_mean_036(self):
        """入：[('🥕', 3), ('🥕', 2), ('🍆', 1), ('🍅', 4), ('🍅', 5), ('🍅', 1)]
           出:('🥕', 2.5) ('🍆', 1.0) ('🍅', 3.3333333333333335)"""
        ApacheFun(data_list_tuple5, data_type=data_type).mean().print()

    def test_sum_037(self):
        ApacheFun(data_list3, data_type=data_type).sum().print()

    def test_sum_038(self):
        ApacheFun(data_list_tuple5, data_type=data_type).sum().print()

    def test_sample_039(self):
        ApacheFun(data_list3, data_type=data_type).sample(2).print()

    def test_sample_040(self):
        ApacheFun(data_list_tuple5, data_type=data_type).sample(2).print()

    def test_top_041(self):
        ApacheFun(data_list3, data_type=data_type).top_largest(2).print()

    def test_top_042(self):
        ApacheFun(data_list_tuple5, data_type=data_type).top_largest(2).print()

    def test_top_043(self):
        ApacheFun(data_list3, data_type=data_type).top_smallest(2).print()

    def test_top_044(self):
        ApacheFun(data_list_tuple5, data_type=data_type).top_smallest(2).print()

    def test_top_045(self):
        ApacheFun(data_list3, data_type=data_type).top_of(2).print()

    def test_top_046(self):
        ApacheFun(data_list_tuple5, data_type=data_type).top_of(1).print()