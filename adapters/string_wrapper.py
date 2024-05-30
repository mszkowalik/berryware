# adapters/string_wrapper.py

def count(s, sub, begin=0, end=None):
    return s.count(sub, begin, end)

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

def find(s, sub, begin=0, end=None):
    return s.find(sub, begin, end)

def startswith(s, sub, case_insensitive=False):
    if case_insensitive:
        return s.lower().startswith(sub.lower())
    return s.startswith(sub)

def endswith(s, sub, case_insensitive=False):
    if case_insensitive:
        return s.lower().endswith(sub.lower())
    return s.endswith(sub)

def hex(number):
    return hex(number)

def byte(s):
    return ord(s[0])

def char(number):
    return chr(number)

def tolower(s):
    return s.lower()

def toupper(s):
    return s.upper()

def tr(s, chars, replacement):
    trans = str.maketrans(chars, replacement)
    return s.translate(trans)

def replace(s, text1, text2):
    return s.replace(text1, text2)

def escape(s, berry_mode=False):
    import json
    if berry_mode:
        return json.dumps(s).replace('"', "'")
    return json.dumps(s)

def format(fmt, *args):
    return fmt % args

# Module's mock usage example
if __name__ == "__main__":
    s = "Hello, World!"
    print(count(s, "o"))               # 2
    print(split(s, 7))                 # ['Hello, ', 'World!']
    print(find(s, "World"))            # 7
    print(startswith(s, "Hello"))      # True
    print(endswith(s, "!"))            # True
    print(hex(255))                    # '0xff'
    print(byte("Hello"))               # 72
    print(char(72))                    # 'H'
    print(tolower("HELLO"))            # 'hello'
    print(toupper("hello"))            # 'HELLO'
    print(tr("hello", "ho", "jy"))     # 'jelly'
    print(replace(s, "World", "there")) # 'Hello, there!'
    print(escape(s))                   # '"Hello, World!"'
    print(escape(s, berry_mode=True))  # '\'Hello, World!\''
    print(format("Hello %s", "World")) # 'Hello World'