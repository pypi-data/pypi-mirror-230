import json

from apache_beam.coders import Coder


class JsonCoder(Coder):
    """A JSON coder interpreting each line as a JSON string."""

    def encode(self, value):
        try:
            value = eval(value)
        except:
            try:
                value = json.dumps(value)
            except:
                value = value.encode('utf-8')
        return value

    def decode(self, value):
        try:
            value = eval(value)
        except:
            try:
                value = json.loads(value)
            except:
                value = value.decode('utf-8')
        return value