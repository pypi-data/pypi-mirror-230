import datetime
import time
import pandas as pd
import apache_beam as beam
import uuid

from apache_beam import PCollection
from apache_beam.io import fileio
from apache_beam.pvalue import DoOutputsTuple
from apache_beam.transforms import window


class ApacheFun:
    window = window

    def __init__(self, data=None, name="", out=None, data_type=1):
        """data_type: 1 管道， 2 数据"""

        self.pipeline = beam.Pipeline()
        self.data = data
        self.out = out
        self.value = None
        self.name = name or str(uuid.uuid4())[-12:]
        self.data_type = data_type
        self._i = 0
        self._tmp_value = None
        self._group_by = None
        self._group_by_old = None
        self._aggregate_field = []
        if data:
            self.create()

    def __str__(self):
        return self.value

    def _name(self):
        self._i += 1
        return str(self.name) + "_" + str(self._i)

    def run(self):
        """执行"""
        self.pipeline.run()

    def print(self, fmt=None):
        """打印"""
        def _print(x):
            if fmt:
                _str = "self._tmp_value=" + fmt
                exec(_str)
                print(self._tmp_value)
            else:
                print(x)
        if isinstance(self.out, PCollection):
            self.out | self._name() >> beam.Map(lambda x: _print(x))
        elif isinstance(self.out, (list, tuple, DoOutputsTuple)):
            for i in self.out:
                if isinstance(i, PCollection):
                    i | self._name() >> beam.Map(lambda x: _print(x))
                else:
                    _print(i)
        if self.data_type == 1:
            self.run()

    # def get_value(self):
    #     class ProcessDataDoFn(beam.DoFn):
    #         def process(self, element, side_input):
    #             output_dictionary = "element"
    #             return output_dictionary

    def set_data(self, data):
        self.data = data
        self.create(data)
        self.out = self.value

    def create(self, data=None):
        """创建"""
        if self.data_type == 1:
            self.value = self.pipeline | self._name() >> beam.Create(data or self.data)
        else:
            self.value = data or self.data
        if not(data and self.data):
            self.out = self.value
        return self

    def par_do(self, fn, *args, **kwargs):
        """ParDo 与 DoFn 方法"""
        self.value = self.out = self.get_out() | self._name() >> beam.ParDo(fn, *args, **kwargs)
        return self

    def window_info(self, fn, *args, **kwargs):
        self.value = self.out = self.get_out() | self._name() >> beam.WindowInto(fn, *args, **kwargs)
        return self

    def get_out(self):
        """判断是否已经是管道"""
        if self.data_type == 1:
            return self.out if isinstance(self.out, PCollection) else self.create().value
        else:
            return self.out

    def map(self, fn, *args, **kwargs):
        """对集合中的每个元素应用简单的 1 对 1 映射函数。"""
        self.value = self.out = self.get_out() | self._name() >> beam.Map(fn, *args, **kwargs)
        return self

    def map_tuple(self, fn, *args, **kwargs):
        """如果PCollection由（键、值）对组成，则可以使用MapTuple将它们解压到不同的函数参数中"""
        self.value = self.out = self.get_out() | self._name() >> beam.MapTuple(fn, *args, **kwargs)
        return self

    def filter(self, fn, *args, **kwargs):
        """给定一个谓词，过滤掉所有不满足该谓词的元素。"""
        self.value = self.out = self.get_out() | self._name() >> beam.Filter(fn, *args, **kwargs)
        return self

    def flat_map(self, fn, *args, **kwargs):
        """应用一个函数，该函数将集合返回到输入中的每个元素，并输出所有结果元素。"""
        self.value = self.out = self.get_out() | self._name() >> beam.FlatMap(fn, *args, **kwargs)
        return self

    def flat_map_tuple(self, fn, *args, **kwargs):
        """应用一个函数，该函数将集合返回到输入中的每个元素，并输出所有结果元素。"""
        self.value = self.out = self.get_out() | self._name() >> beam.FlatMapTuple(fn, *args, **kwargs)
        return self

    def regex_matches(self, regex, group=0):
        """根据正则表达式过滤输入字符串元素，也可以根据匹配的组对它们进行转换。"""
        self.value = self.out = self.get_out() | self._name() >> beam.Regex.matches(regex, group)
        return self

    def regex_all_match(self, regex):
        """根据正则表达式过滤输入字符串元素，也可以根据匹配的组对它们进行转换。"""
        self.value = self.out = self.get_out() | self._name() >> beam.Regex.all_matches(regex)
        return self

    def regex_matches_kv(self, regex, keyGroup=0):
        """根据正则表达式过滤输入字符串元素，也可以根据匹配的组对它们进行转换。"""
        self.value = self.out = self.get_out() | self._name() >> beam.Regex.matches_kv(regex, keyGroup)
        return self

    def regex_find(self, regex, group=0):
        """根据正则表达式过滤输入字符串元素，也可以根据匹配的组对它们进行转换。"""
        self.value = self.out = self.get_out() | self._name() >> beam.Regex.find(regex, group)
        return self

    def regex_find_all(self, regex):
        """根据正则表达式过滤输入字符串元素，也可以根据匹配的组对它们进行转换。"""
        self.value = self.out = self.get_out() | self._name() >> beam.Regex.find_all(regex)
        return self

    def regex_find_kv(self, regex, keyGroup=0):
        """根据正则表达式过滤输入字符串元素，也可以根据匹配的组对它们进行转换。"""
        self.value = self.out = self.get_out() | self._name() >> beam.Regex.find_kv(regex, keyGroup)
        return self

    def regex_replace_all(self, regex, replacement):
        """根据正则表达式过滤输入字符串元素，也可以根据匹配的组对它们进行转换。"""
        self.value = self.out = self.get_out() | self._name() >> beam.Regex.replace_all(regex, replacement)
        return self

    def regex_replace_first(self, regex, replacement):
        """根据正则表达式过滤输入字符串元素，也可以根据匹配的组对它们进行转换。"""
        self.value = self.out = self.get_out() | self._name() >> beam.Regex.replace_first(regex, replacement)
        return self

    def regex_split(self, regex, outputEmpty=False):
        """根据正则表达式过滤输入字符串元素，也可以根据匹配的组对它们进行转换。"""
        self.value = self.out = self.get_out() | self._name() >> beam.Regex.split(regex, outputEmpty)
        return self

    def partition(self, fn, num, *args, **kwargs):
        """基于某些分区函数将每个输入元素路由到特定的输出集合。"""
        self.out = self.get_out() | self._name() >> beam.Partition(fn, num, *args, **kwargs)
        self.value = [ApacheFun(out=x) for x in self.out]
        return self

    def pvalue_as_dict(self, data):
        """字典"""
        return beam.pvalue.AsDict(self.create(data).value) if self.data_type == 1 else {k: v for k, v in data}

    def pvalue_as_iter(self, data):
        """列表"""
        return beam.pvalue.AsIter(self.create(data).value) if self.data_type == 1 else data

    def pvalue_as_singleton(self, data):
        """单实例"""
        data = [data] if isinstance(data, str) else data
        return beam.pvalue.AsSingleton(self.create(data).value) if self.data_type == 1 else data[0]

    def keys(self, data=None):
        self.value = self.create(data).value | self._name() >> beam.Keys()
        if not(data and self.data):
            self.out = self.value
        return self

    def values(self, data=None):
        self.value = self.create(data).value | self._name() >> beam.Values()
        if not (data and self.data):
            self.out = self.value
        return self

    def to_string_kvs(self):
        """将输入集合中的每个元素转换为字符串。"""
        self.value = self.out = self.get_out() | self._name() >> beam.ToString.Kvs()
        return self

    def to_string_element(self):
        """将输入集合中的每个元素转换为字符串。"""
        self.value = self.out = self.get_out() | self._name() >> beam.ToString.Element()
        return self

    def to_string_iterables(self):
        """将输入集合中的每个元素转换为字符串。"""
        self.value = self.out = self.get_out() | self._name() >> beam.ToString.Iterables()
        return self

    def timestamped_value(self, key=None, type="bj", key2=None):
        """应用一个函数来确定输出集合中每个元素的时间戳，并更新与每个输入关联的隐式时间戳。请注意，只有向前调整时间戳才是安全的"""
        class GetTimestamp(beam.DoFn):
            def __init__(self, key=None, key2=None):
                self.key = key
                self.key2 = key2

            def process(self, plant, timestamp=beam.DoFn.TimestampParam):
                key = self.key if self.key else "current"
                if type == "utc":
                    _time = timestamp.to_utc_datetime()
                elif type == "bj":
                    _time = datetime.datetime.fromtimestamp(timestamp.micros / 1e6).strftime("%Y-%m-%d %H:%M:%S")
                elif type == "rfc":
                    _time = timestamp.to_rfc3339()
                elif type == "proto":
                    _time = timestamp.to_proto()
                elif type == "s":
                    _time = timestamp.to_proto().seconds
                elif type == "m":
                    _time = timestamp.to_proto().seconds // 60
                elif type == "h":
                    _time = timestamp.to_proto().seconds // 3600
                elif type in ("t", "d"):
                    _time = timestamp.to_proto().seconds // 3600 // 24
                plant[key] = _time
                yield plant

        def get_key(plant):
            if key and (isinstance(plant, dict) and plant.get(key)):
                _time = plant[key]
            elif key and (isinstance(plant, (list, tuple)) and len(plant) == 2 and
                          isinstance(plant[1], dict) and plant[1].get(key)):
                _time = plant[1][key]
            else:
                _time = time.time()
            if isinstance(_time, (int, float)):
                return _time
            else:
                if len(_time) == 10:
                    return time.mktime(time.strptime(_time, '%Y-%m-%d'))
                elif len(_time) >= 19:
                    return time.mktime(time.strptime(_time[:19], '%Y-%m-%d %H:%M:%S'))

        if self.data_type == 1:
            def get_plant2(plant):
                _plant = plant if not key2 else (plant[0], plant[1][key2])
                return self.window.TimestampedValue(_plant, get_key(plant))
            if key2:
                self.value = self.out = self.get_out() | self._name() >> beam.Map(get_plant2)
            else:
                self.value = self.out = self.get_out() | self._name() >> beam.Map(get_plant2) | self._name() >> beam.ParDo(
                    GetTimestamp(key=key))
        else:
            def get_plant(plant):
                micros = get_key(plant)
                micros = int(int(float(micros)) / (10 ** (len(str(int(float(micros))))-10)))
                if type == "s":
                    plant[key] = micros
                elif type == "m":
                    plant[key] = micros // 60
                elif type == "h":
                    plant[key] = micros // 3600
                elif type in ("t", "d"):
                    plant[key] = micros // 3600 // 24
                else:
                    plant[key] = datetime.datetime.fromtimestamp(micros).strftime("%Y-%m-%d %H:%M:%S")
                return plant
            self.value = self.out = self.get_out() | beam.Map(get_plant)
        return self

    def kvswap(self, data=None):
        """获取一个键值对集合并返回一个键值对集合，其中每个键值对都进行了交换。"""
        self.value = self.create(data).value | self._name() >> beam.KvSwap()
        if not (data and self.data):
            self.out = self.value
        return self

    def co_group_by_key(self, *args, **kwargs):
        """获取多个键控元素集合并生成一个集合，其中每个元素都包含一个键和与该键关联的所有值。"""
        plants = {}
        for i, v in enumerate(args):
            plants["key%s" % i] = v if isinstance(v, PCollection) else (
                v.value if isinstance(v, ApacheFun) else self.create(v).value)
        for k, v in kwargs.items():
            plants[k] = v if isinstance(v, PCollection) else (
                v.value if isinstance(v, ApacheFun) else self.create(v).value)
        self.value = self.out = plants | self._name() >> beam.CoGroupByKey()
        return self

    def combine_globally(self, fn, *args, **kwargs):
        """组合集合中的所有元素"""
        self.value = self.out = self.get_out() | self._name() >> beam.CombineGlobally(fn, *args, **kwargs)
        return self

    def combine_percentages_fn(self, key=None, type=1):
        """统计集合中的所有元素"""
        class PercentagesFn(beam.CombineFn):
            def __init__(self, key=None, type=1):
                self.key = key
                self.type = type

            def create_accumulator(self):
                return {}

            def add_input(self, accumulator, input):
                input = input[self.key] if self.key and self.key in input else input
                if input not in accumulator:
                    accumulator[input] = 0
                accumulator[input] += 1
                return accumulator

            def merge_accumulators(self, accumulators):
                merged = {}
                for accum in accumulators:
                    for item, count in accum.items():
                        if item not in merged:
                            merged[item] = 0
                        merged[item] += count
                return merged

            def extract_output(self, accumulator):
                if self.type == 1:
                    return accumulator
                elif self.type == 2:
                    total = sum(accumulator.values())  # 10
                    percentages = {item: count / total for item, count in accumulator.items()}
                    return percentages
                elif self.type == 3:
                    total = sum(accumulator.values())  # 10
                    percentages = {item: ("%.1f%%" % (count / total * 100)) for item, count in accumulator.items()}
                    return percentages
        self.value = self.out = self.combine_globally(PercentagesFn(key, type)).value
        return self

    def combine_per_key(self, fn, *args, **kwargs):
        """组合集合中每个键的所有元素"""
        self.value = self.out = self.get_out() | self._name() >> beam.CombinePerKey(fn, *args, **kwargs)
        return self

    def combine_values(self, fn, *args, **kwargs):
        """在键控元素集合中组合可迭代的值"""
        self.value = self.out = self.get_out() | self._name() >> beam.CombineValues(fn, *args, **kwargs)
        return self

    def count_globally(self):
        """计算每个聚合中的元素个数"""
        self.value = self.out = self.get_out() | self._name() >> beam.combiners.Count.Globally()
        return self

    def count_per_key(self):
        """计算键值的 PCollection 中每个唯一键的元素"""
        self.value = self.out = self.get_out() | self._name() >> beam.combiners.Count.PerKey()
        return self

    def count_per_element(self):
        """计算PCollection中唯一的元素"""
        self.value = self.out = self.get_out() | self._name() >> beam.combiners.Count.PerElement()
        return self

    def distinct(self):
        """生成一个包含输入集合的不同元素的集合"""
        self.value = self.out = self.get_out() | self._name() >> beam.Distinct()
        return self

    def group_by_key(self):
        """获取元素的键值集合，并生成一个集合，其中每个元素由一个键和与该键关联的所有值组成"""
        self.value = self.out = self.get_out() | self._name() >> beam.GroupByKey()
        return self

    def group_by(self, *fields, **kwargs):
        self._group_by = beam.GroupBy(*fields, **kwargs)
        self._group_by_old = self.get_out()
        self.value = self.out = self._group_by_old | self._name() >> self._group_by
        return self

    def aggregate_field(self, field, combine_fn, dest):
        self._aggregate_field.append((field, combine_fn, dest))
        _group_by = self._group_by if self._group_by else beam.GroupBy()
        self._group_by_old = self._group_by_old if self._group_by_old else self.get_out()
        for i in self._aggregate_field:
            _group_by = _group_by.aggregate_field(*i)
        self.value = self.out = self._group_by_old | self._name() >> _group_by
        return self

    def group_into_batches(self, batch_size):
        self.value = self.out = self.get_out() | self._name() >> beam.GroupIntoBatches(batch_size)
        return self

    def latest_globally(self, key=None):
        if key:
            self.timestamped_value(key)
        self.value = self.out = self.get_out() | self._name() >> beam.combiners.Latest.Globally()
        return self

    def latest_per_key(self, key, latest_key):
        self.timestamped_value(key=key, key2=latest_key)
        self.value = self.out = self.get_out() | self._name() >> beam.combiners.Latest.PerKey()
        return self

    def max(self):
        """最大值"""
        if isinstance(self.data[0], (list, tuple)):
            self.combine_per_key(max)
        else:
            self.combine_globally(max)
        return self

    def min(self):
        """最小值"""
        if isinstance(self.data[0], (list, tuple)):
            self.combine_per_key(min)
        else:
            self.combine_globally(min)
        return self

    def sum(self):
        """求和"""
        if isinstance(self.data[0], (list, tuple)):
            self.combine_per_key(sum)
        else:
            self.combine_globally(sum)
        return self

    def mean(self):
        """平均值"""
        if isinstance(self.data[0], (list, tuple)):
            self.value = self.out = self.get_out() | self._name() >> beam.combiners.Mean.PerKey()
        else:
            self.value = self.out = self.get_out() | self._name() >> beam.combiners.Mean.Globally()
        return self

    def sample(self, n):
        """随机取n个"""
        if isinstance(self.data[0], (list, tuple)):
            self.value = self.out = self.get_out() | self._name() >> beam.combiners.Sample.FixedSizePerKey(n)
        else:
            self.value = self.out = self.get_out() | self._name() >> beam.combiners.Sample.FixedSizeGlobally(n)
        return self

    def top_largest(self, n):
        """取最大的n个"""
        if isinstance(self.data[0], (list, tuple)):
            self.value = self.out = self.get_out() | self._name() >> beam.combiners.Top.LargestPerKey(n)
        else:
            self.value = self.out = self.get_out() | self._name() >> beam.combiners.Top.Largest(n)
        return self

    def top_smallest(self, n):
        """取最小的n个"""
        if isinstance(self.data[0], (list, tuple)):
            self.value = self.out = self.get_out() | self._name() >> beam.combiners.Top.SmallestPerKey(n)
        else:
            self.value = self.out = self.get_out() | self._name() >> beam.combiners.Top.Smallest(n)
        return self

    def top_of(self, n, key=None, reverse=True):
        """取前n个"""
        if isinstance(self.data[0], (list, tuple)):
            self.value = self.out = self.get_out() | self._name() >> beam.combiners.Top.PerKey(n, key, reverse=reverse)
        else:
            self.value = self.out = self.get_out() | self._name() >> beam.combiners.Top.Of(n, key, reverse=reverse)
        return self

    def read_excel(self, file_path, sheet_name=0):
        def process_excel_file(element):
            file_name = element.metadata.path
            df = pd.read_excel(file_name, sheet_name)
            return df.values.tolist()
        self.value = self.out = (
                self.pipeline
                | self._name() >> beam.io.fileio.MatchFiles(file_path)
                | self._name() >> beam.io.fileio.ReadMatches()
                | self._name() >> beam.Map(process_excel_file))
        return self

    def write_excel(self, file_path):
        def process_excel_file(element):
            file_name = element.metadata.path
            info = pd.DataFrame()
        self.value = self.out = (
                self.pipeline
                | self._name() >> beam.io.fileio.MatchFiles(file_path)
                | self._name() >> beam.Map(process_excel_file))
        #         beam.io.fileio.WriteToFiles( path=file_path,
        # output_fn=pd.to_excel(file_name, sheet_name)
        #   file_naming=beam.io.fileio.destination_prefix_naming(suffix=".xlsx"))
        #  )
        # beam.io.ReadFromText
        return self

    def read_file(self, path):
        if path.split(".")[-1] in ("txt", "py", "csv"):
            self.value = self.out = self.pipeline | self._name() >> beam.io.ReadFromText(path)
        elif path.split(".")[-1] == "json":
            self.value = self.out = self.pipeline | self._name() >> beam.io.ReadFromJson(path, dtype=False, encodings='utf-8')

        return self



if __name__ == '__main__':
    path = r"C:\Users\hangkai.hu\Desktop\测试\雷达用例\111.txt"
    path = r"C:\Users\hangkai.hu\Desktop\测试\雷达用例\222.json"
    ApacheFun().read_file(path).print()
