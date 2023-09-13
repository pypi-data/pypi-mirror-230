import apache_beam as beam
from apache_beam.transforms import window


class SplitWords(beam.DoFn):
    def __init__(self, delimiter=','):
        self.delimiter = delimiter

    def process(self, text):
        for word in text.split(self.delimiter):
            yield word


class AnalyzeElement(beam.DoFn):
  def process(
      self,
      elem,
      timestamp=beam.DoFn.TimestampParam,
      window=beam.DoFn.WindowParam):
    yield '\n'.join([
        '# timestamp',
        'type(timestamp) -> ' + repr(type(timestamp)),
        'timestamp.micros -> ' + repr(timestamp.micros),
        'timestamp.to_rfc3339() -> ' + repr(timestamp.to_rfc3339()),
        'timestamp.to_utc_datetime() -> ' + repr(timestamp.to_utc_datetime()),
        '',
        '# window',
        'type(window) -> ' + repr(type(window)),
        'window.start -> {} ({})'.format(
            window.start, window.start.to_utc_datetime()),
        'window.end -> {} ({})'.format(
            window.end, window.end.to_utc_datetime()),
        'window.max_timestamp() -> {} ({})'.format(
            window.max_timestamp(), window.max_timestamp().to_utc_datetime()),
    ])


class DoFnMethods(beam.DoFn):
  def __init__(self):
    print('__init__')
    self.window = window.GlobalWindow()

  def setup(self):
    print('setup')

  def start_bundle(self):
    print('start_bundle')

  def process(self, element, window=beam.DoFn.WindowParam):
    self.window = window
    yield '* process: ' + element

  def finish_bundle(self):
    yield beam.utils.windowed_value.WindowedValue(
        value='* finish_bundle: 🌱🌳🌍',
        timestamp=0,
        windows=[self.window],
    )

  def teardown(self):
    print('teardown')


class AverageFn(beam.CombineFn):
  def create_accumulator(self):
    sum = 0.0
    count = 0
    accumulator = sum, count
    return accumulator

  def add_input(self, accumulator, input):
    sum, count = accumulator
    return sum + input, count + 1

  def merge_accumulators(self, accumulators):
    sums, counts = zip(*accumulators)
    return sum(sums), sum(counts)

  def extract_output(self, accumulator):
    sum, count = accumulator
    if count == 0:
      return float('NaN')
    return sum / count


class AverageFn2(beam.CombineFn):
  def create_accumulator(self):
    return {}

  def add_input(self, accumulator, input):
    # accumulator == {}
    # input == '🥕'
    if input not in accumulator:
      accumulator[input] = 0  # {'🥕': 0}
    accumulator[input] += 1  # {'🥕': 1}
    return accumulator

  def merge_accumulators(self, accumulators):
    # accumulators == [
    #     {'🥕': 1, '🍅': 1},
    #     {'🥕': 1, '🍅': 1, '🍆': 1},
    # ]
    merged = {}
    for accum in accumulators:
      for item, count in accum.items():
        if item not in merged:
          merged[item] = 0
        merged[item] += count
    # merged == {'🥕': 2, '🍅': 2, '🍆': 1}
    return merged

  def extract_output(self, accumulator):
    # accumulator == {'🥕': 2, '🍅': 2, '🍆': 1}
    total = sum(accumulator.values())  # 5
    percentages = {item: count / total for item, count in accumulator.items()}
    # percentages == {'🥕': 0.4, '🍅': 0.4, '🍆': 0.2}
    return percentages

