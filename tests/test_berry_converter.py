import unittest
from berry_converter import PythonToBerryConverter

class TestPythonToBerryConverter(unittest.TestCase):
    def setUp(self):
        self.converter = PythonToBerryConverter()

    def test_class_and_function_conversion(self):
        source_code = """
class TestClass:
    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2

    def test_method(self):
        return self.param1 + self.param2
"""
        expected_output = """
class TestClass
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
if not (self.collect_data or self.hems_collect_data or self.hems_check_data):
    self.do_something()
elif self.check_data:
    self.do_something_else()
else:
    self.default_action()
"""
        expected_output = """
if not(self.collect_data or self.hems_collect_data or self.hems_check_data)
    self.do_something()
elif self.check_data
    self.do_something_else()
else
    self.default_action()
end"""
        berry_code = self.converter.convert(source_code)
        self.assertEqual(berry_code.strip(), expected_output.strip())


    def test_augmented_assignment_conversion(self):
        source_code = """
self.i += 1
"""
        expected_output = """self.i += 1"""
        berry_code = self.converter.convert(source_code)
        self.assertEqual(berry_code.strip(), expected_output.strip())

    def test_string_formatting_conversion(self):
        source_code = """
self.web_msg = string.format('<h2>Monitoring Data: </h2><textarea name="message" rows="%d" cols="30" readonly>Waiting for data...</textarea>', self.sequencer.size() + 2)
"""
        expected_output = """self.web_msg = string.format('<h2>Monitoring Data: </h2><textarea name="message" rows="%d" cols="30" readonly>Waiting for data...</textarea>', self.sequencer.size() + 2)"""
        berry_code = self.converter.convert(source_code)
        self.assertEqual(berry_code.strip(), expected_output.strip())

    def test_f_string_conversion(self):
        source_code = """
self.mqtt_topic_config = f"tele/{self.EUI}/{mqtt_topic_config}"
"""
        expected_output = """self.mqtt_topic_config = string.format('tele/%s/%s', self.EUI, mqtt_topic_config)"""
        berry_code = self.converter.convert(source_code)
        self.assertEqual(berry_code.strip(), expected_output.strip())

    def test_dictionary_conversion(self):
        source_code = """
self.address_map = {
    "3034": {"name": 'PV-V-A', "functioncode": 4, "type": "uint16", "count": 1, "sum": 0}
}
"""
        expected_output = """self.address_map = {'3034': {'name': 'PV-V-A', 'functioncode': 4, 'type': 'uint16', 'count': 1, 'sum': 0}}"""
        berry_code = self.converter.convert(source_code)
        self.assertEqual(berry_code.strip(), expected_output.strip())

    def test_list_conversion(self):
        source_code = """
self.hems_sequencer = []
"""
        expected_output = """self.hems_sequencer = []"""
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
try:
    self.mqtt_data()
except Exception as error_msg:
    print("Wrong mqtt query: ", error_msg)
"""
        expected_output = """
try
    self.mqtt_data()
except .. as error_msg
    print('Wrong mqtt query: ', error_msg)
end"""
        berry_code = self.converter.convert(source_code)
        print(f"DEBUG: Berry code generated: {berry_code}")
        self.assertEqual(berry_code.strip(), expected_output.strip())

    def test_multiline_string_print(self):
        source_code = """
print('Finished collecting data:\\n', self.json_response)
"""
        expected_output = """
print('Finished collecting data:\\n', self.json_response)
"""
        berry_code = self.converter.convert(source_code)
        print(f"DEBUG: Berry code generated: {berry_code}")
        self.assertEqual(berry_code.strip(), expected_output.strip())

if __name__ == '__main__':
    unittest.main()
