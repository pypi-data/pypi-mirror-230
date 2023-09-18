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