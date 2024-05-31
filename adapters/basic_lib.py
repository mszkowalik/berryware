# adapters/basic_lib.py

import json as std_json
import math as std_math
import random
import time as std_time
import builtins

# Built-in functions

def custom_print(*args):
    builtins.print(*args)

def custom_input(prompt=''):
    return builtins.input(prompt)

def classname(obj):
    if isinstance(obj, type):
        return obj.__name__
    if hasattr(obj, '__class__'):
        return obj.__class__.__name__
    return None

def classof(obj):
    return obj.__class__ if hasattr(obj, '__class__') else None

def custom_str(value):
    return builtins.str(value)

def number(value):
    try:
        return float(value) if '.' in builtins.str(value) else int(value)
    except ValueError:
        return None

def custom_int(value):
    try:
        return builtins.int(value, 0)
    except ValueError:
        return None

def real(value):
    try:
        return float(value)
    except ValueError:
        return None

def custom_bool(value):
    return builtins.bool(value)

def custom_type(value):
    return builtins.type(value).__name__

def custom_size(value):
    if isinstance(value, (str, list, dict)):
        return len(value)
    return 0

def custom_super(obj):
    return builtins.super(obj.__class__, obj)

def custom_assert(expression, message="Assert Failed"):
    if not expression:
        raise AssertionError(message)

def custom_compile(source, mode='string'):
    if mode == 'file':
        with open(source, 'r') as f:
            source = f.read()
    return builtins.compile(source, '<string>', 'exec')

# JSON Module
# List class
class List:
    def __init__(self, *args):
        self.data = list(args)

    def tostring(self):
        return str(self.data)

    def concat(self, sep=''):
        return sep.join(map(str, self.data))

    def push(self, value):
        self.data.append(value)

    def pop(self, index=-1):
        return self.data.pop(index)

    def insert(self, index, value):
        self.data.insert(index, value)

    def remove(self, index):
        return self.data.pop(index)

    def item(self, index):
        return self.data[index]

    def setitem(self, index, value):
        self.data[index] = value

    def size(self):
        return len(self.data)

    def resize(self, count):
        if count < len(self.data):
            self.data = self.data[:count]
        else:
            self.data.extend([None] * (count - len(self.data)))

    def iter(self):
        return iter(self.data)

    def find(self, index):
        try:
            return self.data[index]
        except IndexError:
            return None

    def reverse(self):
        self.data.reverse()
        return self.data


# Map class
class Map:
    def __init__(self):
        self.data = {}

    def tostring(self):
        return str(self.data)

    def insert(self, key, value):
        self.data[key] = value
        return True

    def remove(self, key):
        return self.data.pop(key, None)

    def item(self, key):
        return self.data.get(key)

    def setitem(self, key, value):
        self.data[key] = value

    def size(self):
        return len(self.data)

    def contains(self, key):
        return key in self.data

    def find(self, key, default=None):
        return self.data.get(key, default)

    def keys(self):
        return iter(self.data.keys())


# Range class
class Range:
    def __init__(self, start, end=None):
        if end is None:
            end = start
            start = 0
        self.data = range(start, end + 1)

    def __iter__(self):
        return iter(self.data)


# Bytes class
class Bytes:
    def __init__(self, initial=None, size=None):
        if isinstance(initial, str):
            self.data = bytearray.fromhex(initial)
        elif isinstance(initial, int):
            self.data = bytearray(initial)
        elif initial is None:
            self.data = bytearray()
        else:
            self.data = bytearray()

    def size(self):
        return len(self.data)

    def tostring(self, max_bytes=None):
        if max_bytes is None:
            max_bytes = len(self.data)
        return 'bytes(' + ''.join('{:02x}'.format(b) for b in self.data[:max_bytes]) + ')'

    def tohex(self):
        return ''.join('{:02x}'.format(b) for b in self.data)

    def fromhex(self, hexstr):
        self.data = bytearray.fromhex(hexstr)

    def clear(self):
        self.data.clear()

    def resize(self, new_size):
        if new_size < len(self.data):
            self.data = self.data[:new_size]
        else:
            self.data.extend(bytearray(new_size - len(self.data)))

    def __getitem__(self, index):
        if isinstance(index, slice):
            return Bytes(self.data[index])
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value

    def copy(self):
        return Bytes(self.tohex())

    def get(self, offset, size):
        if size > 0:
            return int.from_bytes(self.data[offset:offset + size], 'little')
        return int.from_bytes(self.data[offset:offset + abs(size)], 'big')

    def set(self, offset, value, size):
        if size > 0:
            self.data[offset:offset + size] = value.to_bytes(size, 'little')
        else:
            self.data[offset:offset + abs(size)] = value.to_bytes(abs(size), 'big')

    def add(self, value, size):
        if size > 0:
            self.data.extend(value.to_bytes(size, 'little'))
        else:
            self.data.extend(value.to_bytes(abs(size), 'big'))

    def asstring(self):
        return self.data.decode('latin1')

    def fromstring(self, string):
        self.data = bytearray(string, 'latin1')

    def setbits(self, offset, length, value):
        for i in range(length):
            bit = (value >> i) & 1
            byte_index = (offset + i) // 8
            bit_index = (offset + i) % 8
            self.data[byte_index] = (self.data[byte_index] & ~(1 << bit_index)) | (bit << bit_index)

    def getbits(self, offset, length):
        result = 0
        for i in range(length):
            byte_index = (offset + i) // 8
            bit_index = (offset + i) % 8
            bit = (self.data[byte_index] >> bit_index) & 1
            result |= (bit << i)
        return result

    def tob64(self):
        import base64
        return base64.b64encode(self.data).decode('ascii')

    def fromb64(self, b64str):
        import base64
        self.data = bytearray(base64.b64decode(b64str))

    def getfloat(self, offset):
        import struct
        return struct.unpack('f', self.data[offset:offset + 4])[0]

    def setfloat(self, offset, value):
        import struct
        self.data[offset:offset + 4] = struct.pack('f', value)

    def _buffer(self):
        return self.data

    def _change_buffer(self, new_buffer):
        self.data = bytearray(new_buffer)


# JSON Module
class JSONModule:
    @staticmethod
    def load(text):
        try:
            return std_json.loads(text)
        except std_json.JSONDecodeError:
            return None

    @staticmethod
    def dump(obj, format=False):
        if format:
            return std_json.dumps(obj, indent=4)
        return std_json.dumps(obj)


# Math Module
class MathModule:
    pi = std_math.pi

    @staticmethod
    def abs(value):
        return std_math.fabs(value)

    @staticmethod
    def ceil(value):
        return std_math.ceil(value)

    @staticmethod
    def floor(value):
        return std_math.floor(value)

    @staticmethod
    def sin(value):
        return std_math.sin(value)

    @staticmethod
    def cos(value):
        return std_math.cos(value)

    @staticmethod
    def tan(value):
        return std_math.tan(value)

    @staticmethod
    def asin(value):
        return std_math.asin(value)

    @staticmethod
    def acos(value):
        return std_math.acos(value)

    @staticmethod
    def atan(value):
        return std_math.atan(value)

    @staticmethod
    def sinh(value):
        return std_math.sinh(value)

    @staticmethod
    def cosh(value):
        return std_math.cosh(value)

    @staticmethod
    def tanh(value):
        return std_math.tanh(value)

    @staticmethod
    def sqrt(value):
        return std_math.sqrt(value)

    @staticmethod
    def exp(value):
        return std_math.exp(value)

    @staticmethod
    def log(value):
        return std_math.log(value)

    @staticmethod
    def log10(value):
        return std_math.log10(value)

    @staticmethod
    def deg(value):
        return std_math.degrees(value)

    @staticmethod
    def rad(value):
        return std_math.radians(value)

    @staticmethod
    def pow(x, y):
        return std_math.pow(x, y)

    @staticmethod
    def srand(value):
        random.seed(value)

    @staticmethod
    def rand():
        return random.randint(0, 100)

class TimeModule:
    @staticmethod
    def time():
        return std_time.time()

    @staticmethod
    def dump(ts):
        tm = std_time.gmtime(ts)
        return {
            'year': tm.tm_year,
            'month': tm.tm_mon,
            'day': tm.tm_mday,
            'hour': tm.tm_hour,
            'min': tm.tm_min,
            'sec': tm.tm_sec,
            'weekday': tm.tm_wday + 1  # Make Sunday=1, ..., Saturday=7
        }

    @staticmethod
    def clock():
        return std_time.perf_counter()

# adapters/string_wrapper.py
class StringModule:

    @staticmethod
    def count(s, sub, begin=0, end=None):
        return s.count(sub, begin, end)

    @staticmethod
    def split(s, *args):
        if len(args) == 1:
            pos = args[0]
            return [s[:pos], s[pos:]]
        elif len(args) == 2:
            sep, num = args
            return s.split(sep, num)
        else:
            sep = args[0]
            return s.split(sep)

    @staticmethod
    def find(s, sub, begin=0, end=None):
        return s.find(sub, begin, end)

    @staticmethod
    def startswith(s, sub, case_insensitive=False):
        if case_insensitive:
            return s.lower().startswith(sub.lower())
        return s.startswith(sub)

    @staticmethod
    def endswith(s, sub, case_insensitive=False):
        if case_insensitive:
            return s.lower().endswith(sub.lower())
        return s.endswith(sub)

    @staticmethod
    def hex(number):
        return hex(number)

    @staticmethod
    def byte(s):
        return ord(s[0])

    @staticmethod
    def char(number):
        return chr(number)

    @staticmethod
    def tolower(s):
        return s.lower()

    @staticmethod
    def toupper(s):
        return s.upper()

    @staticmethod
    def tr(s, chars, replacement):
        trans = str.maketrans(chars, replacement)
        return s.translate(trans)

    @staticmethod
    def replace(s, text1, text2):
        return s.replace(text1, text2)

    @staticmethod
    def escape(s, berry_mode=False):
        import json
        if berry_mode:
            return json.dumps(s).replace('"', "'")
        return json.dumps(s)

    @staticmethod
    def format(fmt, *args):
        return fmt % args
