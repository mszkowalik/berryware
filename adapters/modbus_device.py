import json
import random

class ModbusDevice:
    def __init__(self, name, manufacturer, part_number, register_table):
        self.name = name
        self.manufacturer = manufacturer
        self.part_number = part_number
        self.register_table = register_table
        self.error_rate = 0
        self.is_working = True

    def set_error_rate(self, error_rate):
        self.error_rate = error_rate

    def set_working(self, is_working):
        self.is_working = is_working

    def get_register(self, start_address, count):
        register_values = []
        for offset in range(count):
            address = str(int(start_address) + offset)
            if address in self.register_table:
                register_values.append(self.register_table[address]['sum'])
            else:
                register_values.append(0)
        return register_values

    def get_response(self, device_address, function_code, start_address, count):
        if not self.is_working or random.random() < self.error_rate:
            return None

        values = self.get_register(start_address, count)
        response = {
            "DeviceAddress": device_address,
            "FunctionCode": function_code,
            "StartAddress": start_address,
            "Length": count,
            "Count": count,
            "Values": values
        }
        return response
