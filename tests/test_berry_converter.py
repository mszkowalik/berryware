import unittest
from berry_converter import PythonToBerryConverter

class TestPythonToBerryConverter(unittest.TestCase):
    def setUp(self):
        self.converter = PythonToBerryConverter()
        self.maxDiff = None

    def test_class_and_function_conversion(self):
        source_code = """
class TestClass:
    param1 = None
    param2 = 3
    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2

    def test_method(self):
        return self.param1 + self.param2
"""
        expected_output = """
class TestClass
    var param1 = nil
    var param2 = 3
    def init(param1, param2)
        self.param1 = param1
        self.param2 = param2
    end
    def test_method()
        return self.param1 + self.param2
    end
end"""
        berry_code = self.converter.convert(source_code)
        self.assertEqual(berry_code.strip(), expected_output.strip())

    def test_if_else_conversion(self):
        source_code = """
value = 0
value2 = True
value3 = False
if not (value or value2 or value3):
    do_something()
elif check_data:
    do_something_else()
else:
    default_action()
"""
        expected_output = """
var value = 0
var value2 = True
var value3 = False
if not(value or value2 or value3)
    do_something()
elif check_data
    do_something_else()
else
    default_action()
end"""
        berry_code = self.converter.convert(source_code)
        self.assertEqual(berry_code.strip(), expected_output.strip())

    def test_augmented_assignment_conversion(self):
        source_code = """
i = 0
i += 1
"""
        expected_output = """
var i = 0
i += 1"""
        berry_code = self.converter.convert(source_code)
        self.assertEqual(berry_code.strip(), expected_output.strip())

    def test_string_formatting_conversion(self):
        source_code = """
sequencer = 3
web_msg = string.format('<h2>Monitoring Data: </h2><textarea name="message" rows="%d" cols="30" readonly>Waiting for data...</textarea>', sequencer + 2)
"""
        expected_output = """
var sequencer = 3
var web_msg = string.format('<h2>Monitoring Data: </h2><textarea name="message" rows="%d" cols="30" readonly>Waiting for data...</textarea>', sequencer + 2)"""
        berry_code = self.converter.convert(source_code)
        self.assertEqual(berry_code.strip(), expected_output.strip())

    def test_f_string_conversion(self):
        source_code = """
mqtt_topic_config = f"tele/{self.EUI}/{mqtt_topic_config}"
"""
        expected_output = """var mqtt_topic_config = string.format('tele/%s/%s', self.EUI, mqtt_topic_config)"""
        berry_code = self.converter.convert(source_code)
        self.assertEqual(berry_code.strip(), expected_output.strip())

    def test_dictionary_conversion(self):
        source_code = """
address_map = {}
address_map = {
    "3034": {"name": 'PV-V-A', "functioncode": 4, "type": "uint16", "count": 1, "sum": 0}
}
"""
        expected_output = """
var address_map = {}
address_map = {'3034': {'name': 'PV-V-A', 'functioncode': 4, 'type': 'uint16', 'count': 1, 'sum': 0}}"""
        berry_code = self.converter.convert(source_code)
        print(f"DEBUG: Berry code generated: {berry_code}")
        self.assertEqual(berry_code.strip(), expected_output.strip())

    def test_list_conversion(self):
        source_code = """
hems_sequencer = []
"""
        expected_output = """var hems_sequencer = []"""
        berry_code = self.converter.convert(source_code)
        self.assertEqual(berry_code.strip(), expected_output.strip())

    def test_contains_conversion(self):
        source_code = """
if "mode" in msg:
    self.handle_mode()
"""
        expected_output = """if (msg.contains('mode'))
    self.handle_mode()
end"""
        berry_code = self.converter.convert(source_code)
        self.assertEqual(berry_code.strip(), expected_output.strip())

    def test_is_not_conversion(self):
        source_code = """
if delay is not None:
    self.set_delay(delay)
"""
        expected_output = """if delay != nil
    self.set_delay(delay)
end"""
        berry_code = self.converter.convert(source_code)
        self.assertEqual(berry_code.strip(), expected_output.strip())

    def test_exception_handling(self):
        source_code = """
def mqtt_data():
    return True

try:
    mqtt_data()
except Exception as error_msg:
    print("Wrong mqtt query: ", error_msg)
"""
        expected_output = """
def mqtt_data()
    return True
end
try
    mqtt_data()
except .. as error_msg
    print('Wrong mqtt query: ', error_msg)
end"""
        berry_code = self.converter.convert(source_code)
        print(f"DEBUG: Berry code generated: {berry_code}")
        self.assertEqual(berry_code.strip(), expected_output.strip())

    def test_multiline_string_print(self):
        source_code = """
json_response = "some response"
print('Finished collecting data:\\n', json_response)
"""
        expected_output = """
var json_response = 'some response'
print('Finished collecting data:\\n', json_response)
"""
        berry_code = self.converter.convert(source_code)
        print(f"DEBUG: Berry code generated: {berry_code}")
        self.assertEqual(berry_code.strip(), expected_output.strip())

    def test_function_callback_conversion(self):
        source_code = """
class TestClass:
    interval = None
    timer = None

    def __init__(self, interval, timer):
        self.interval = interval
        self.timer = timer

    def start_over(self):
        print("Starting over")

    def set_timers(self):
        tasmota.set_timer(self.interval * 1000, self.start_over, self.timer)
        tasmota.set_timer(self.interval, self.start_over, self.timer)
"""
        expected_output = """
class TestClass
    var interval = nil
    var timer = nil
    def init(interval, timer)
        self.interval = interval
        self.timer = timer
    end
    def start_over()
        print('Starting over')
    end
    def set_timers()
        tasmota.set_timer(self.interval * 1000, /-> self.start_over(), self.timer)
        tasmota.set_timer(self.interval, /-> self.start_over(), self.timer)
    end
end"""
        berry_code = self.converter.convert(source_code)
        print(f"DEBUG: Berry code generated: {berry_code}")
        self.assertEqual(berry_code.strip(), expected_output.strip())

    def test_parentheses(self):
        source_code = """
if (self.value == self.value2):
    self.do_something()
if self.value == self.value2:
    self.do_something()
"""
        expected_output = """
if self.value == self.value2
    self.do_something()
end
if self.value == self.value2
    self.do_something()
end"""
        berry_code = self.converter.convert(source_code)
        print(f"DEBUG: Berry code generated: {berry_code}")
        self.assertEqual(berry_code.strip(), expected_output.strip())

if __name__ == '__main__':
    unittest.main()
