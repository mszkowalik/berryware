# test_tasmota_adapter.py

import unittest
from unittest.mock import patch, MagicMock
import os
import shutil
from adapters.tasmota_adapter import TasmotaAdapter
from adapters.mqtt_adapter import MQTTAdapter
from adapters.modbus_device import ModbusDevice

class TestTasmotaAdapter(unittest.TestCase):
    def setUp(self):
        self.tasmota = TasmotaAdapter("EUI53EF3GD")
        self.mqtt = self.tasmota.mqtt
        self.device = ModbusDevice("TestDevice", "TestManufacturer", "TestPartNumber", {
            "33049": {"name": 'PV-V-A', "functioncode": 4, "type": "uint16", "count": 1, "sum": 10},
        })
        self.tasmota.add_device(self.device)
        self.received_messages = []
        self.mqtt.subscribe(f"tele/EUI53EF3GD/ModbusReceived", self.on_message)

        # Create filesystem directory if it doesn't exist
        if not os.path.exists('filesystem'):
            os.makedirs('filesystem')

    def tearDown(self):
        # Clean up the filesystem directory after tests
        if os.path.exists('filesystem'):
            shutil.rmtree('filesystem')

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

        observed_error_rate = 1 - (success_count / attempts)
        self.assertAlmostEqual(observed_error_rate, error_rate, delta=0.05)

    @patch('requests.get')
    def test_urlfetch(self, mock_get):
        mock_response = MagicMock()
        mock_response.iter_content = lambda chunk_size: [b'test data']
        mock_response.raise_for_status = lambda: None
        mock_get.return_value = mock_response

        url = "http://example.com/testfile"
        filename = "testfile"
        expected_file_path = os.path.join('filesystem', filename)

        bytes_downloaded = self.tasmota.urlfetch(url)

        self.assertEqual(bytes_downloaded, len(b'test data'))
        self.assertTrue(os.path.exists(expected_file_path))

        with open(expected_file_path, 'rb') as f:
            self.assertEqual(f.read(), b'test data')

    def test_add_rule(self):
        def dummy_rule(cmd, idx, payload, raw):
            pass

        self.tasmota.add_rule("test_trigger", dummy_rule, id="test_rule")
        self.assertIn("test_trigger", self.tasmota.rules)
        self.assertEqual(len(self.tasmota.rules["test_trigger"]), 1)
        self.assertEqual(self.tasmota.rules["test_trigger"][0]['id'], "test_rule")

    def test_remove_rule(self):
        def dummy_rule(cmd, idx, payload, raw):
            pass

        self.tasmota.add_rule("test_trigger", dummy_rule, id="test_rule")
        self.tasmota.remove_rule("test_trigger", id="test_rule")
        self.assertNotIn("test_trigger", self.tasmota.rules)

    def test_memory(self):
        memory_stats = self.tasmota.memory()
        self.assertIsInstance(memory_stats, dict)
        self.assertIn('iram_free', memory_stats)

        heap_free = self.tasmota.memory('heap_free')
        self.assertEqual(heap_free, 226)

    def test_gc(self):
        allocated_bytes = self.tasmota.gc()
        self.assertEqual(allocated_bytes, self.tasmota.heap)

    def test_publish_result(self):
        payload = '{"status": "ok"}'
        subtopic = "status"
        received_messages = []

        def on_message(topic, message):
            received_messages.append((topic, message))

        topic = f"tele/{self.tasmota.EUI}/{subtopic}"

        self.mqtt.subscribe(topic, on_message)
        self.mqtt.publish(topic, payload)

        self.assertEqual(len(received_messages), 1)
        self.assertEqual(received_messages[0], (f"tele/{self.tasmota.EUI}/{subtopic}", payload))

    def test_publish_rule(self):
        payload = '{"rule": "test"}'
        handled = self.tasmota.publish_rule(payload)
        self.assertTrue(handled)

if __name__ == '__main__':
    unittest.main()
