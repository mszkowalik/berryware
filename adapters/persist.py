# persist.py
import json
import os
from adapters.singleton import singleton

@singleton
class Persist:
    def __init__(self, filename="_persist.json"):
        self.filename = filename
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                return json.load(file)
        return {}

    def save(self):
        with open(self.filename, 'w') as file:
            json.dump(self.data, file)

    def has(self, key):
        return key in self.data

    def remove(self, key):
        if key in self.data:
            del self.data[key]
            return True
        return False

    def find(self, key, default_value=None):
        return self.data.get(key, default_value)

    def member(self, key):
        return self.data.get(key, None)

    def setmember(self, key, value):
        self.data[key] = value

    def zero(self):
        self.data.clear()

    def __setattr__(self, key, value):
        if key in ("filename", "data"):
            super().__setattr__(key, value)
        else:
            self.data[key] = value

    def __getattr__(self, key):
        if key in ("filename", "data"):
            return super().__getattr__(key)
        else:
            return self.data.get(key, None)

    def __str__(self):
        return str(self.data)


persist = Persist()
