# adapters/json_wrapper.py

import json

class JSONWrapper:
    @staticmethod
    def load(s):
        # Assuming `s` is a string, use `json.loads` to parse it
        return json.loads(s)

    @staticmethod
    def dump(obj):
        # Convert the object to a JSON string
        return json.dumps(obj)