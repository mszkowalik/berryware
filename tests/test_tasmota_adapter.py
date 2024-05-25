# test_tasmota_adapter.py

import unittest
from adapters.tasmota_adapter import TasmotaAdapter
from adapters.mqtt_adapter import MQTTAdapter
from adapters.modbus_device import ModbusDevice

class TestErrorRate(unittest.TestCase):
    def setUp(self):
        self.mqtt = MQTTAdapter()
        self.tasmota = TasmotaAdapter("EUI53EF3GD")
        self.device = ModbusDevice("TestDevice", "TestManufacturer", "TestPartNumber", {
            "33049": {"name": 'PV-V-A', "functioncode": 4, "type": "uint16", "count": 1, "sum": 10},
        })
        self.tasmota.add_device(self.device)
        self.received_messages = []
        self.mqtt.subscribe(f"tele/EUI53EF3GD/ModbusReceived", self.on_message)

    def on_message(self, topic, message):
        self.received_messages.append((topic, message))

    def test_set_device_working(self):
        self.device.set_working(False)
        command = {
            "ModBusSend": {
                "deviceaddress": 2,
                "functioncode": 4,
                "startaddress": 33049,
                "count": 1
            }
        }

        self.mqtt.publish(f"cmnd/EUI53EF3GD/ModbusSend", command)

        self.assertEqual(len(self.received_messages), 0)

    def test_error_rate(self):
        error_rate = 0.5
        self.device.set_error_rate(error_rate)
        command = {
            "ModBusSend": {
                "deviceaddress": 2,
                "functioncode": 4,
                "startaddress": 33049,
                "count": 1
            }
        }

        success_count = 0
        attempts = 1000

        def on_message(topic, message):
            nonlocal success_count
            if topic == f"tele/{self.tasmota.EUI}/ModbusReceived":
                success_count += 1

        self.mqtt.subscribe(f"tele/{self.tasmota.EUI}/ModbusReceived", on_message)

        for _ in range(attempts):
            self.tasmota.cmd(command)

        error_rate = 1 - (success_count / attempts)
        self.assertAlmostEqual(error_rate, error_rate, delta=0.05)

tasmota = TasmotaAdapter("EUI53EF3GD")

if __name__ == '__main__':
    unittest.main()
