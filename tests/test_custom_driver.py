# test_custom_driver.py

import unittest
import threading
import time
from adapters.tasmota_adapter import TasmotaAdapter
from custom_driver import CustomDriver

class TestCustomDriver(unittest.TestCase):
    def setUp(self):
        # Initialize the TasmotaAdapter and register the CustomDriver
        self.tasmota = TasmotaAdapter("EUI53EF3GD")
        self.driver = CustomDriver()
        self.tasmota.add_driver(self.driver)
        self.autoexec_thread = threading.Thread(target=self.run_tasmota)
        self.autoexec_thread.daemon = True  # Allows thread to be killed when main thread exits

    def run_tasmota(self):
        self.tasmota.start()

    def run_autoexec_for_duration(self, duration):
        self.autoexec_thread.start()
        time.sleep(duration)
        print("Stopping TasmotaAdapter after duration")
        # Stopping TasmotaAdapter
        self.tasmota.stop()

    def test_run_custom_driver(self):
        # Run TasmotaAdapter for a specified duration and simulate device operations
        self.run_autoexec_for_duration(5)  # Run for 5 seconds

        # Check that the driver's methods were called
        self.assertTrue(self.driver.counter_50ms > 0, "Driver's every_50ms should have been called")
        self.assertTrue(self.driver.counter_100ms > 0, "Driver's every_100ms should have been called")
        self.assertTrue(self.driver.counter_250ms > 0, "Driver's every_250ms should have been called")
        self.assertTrue(self.driver.counter_second > 0, "Driver's every_second should have been called")

    def test_button_pressed(self):
        self.tasmota.button_pressed()
        self.assertEqual(self.driver.button_press_count, 1, "Driver's button_pressed should have been called once")

    def test_mqtt_data(self):
        topic = "test/topic"
        message = "test message"
        self.tasmota.mqtt.publish(topic, message)
        time.sleep(1)  # Ensure the message is processed
        self.assertIn((topic, message), self.driver.mqtt_messages, "Driver's mqtt_data should have received the message")

    def test_save_before_restart(self):
        self.tasmota.stop()
        self.assertTrue(self.driver.save_before_restart_called, "Driver's save_before_restart should have been called")

    def tearDown(self):
        # Cleanup code after each test
        if self.autoexec_thread.is_alive():
            print("Terminating autoexec thread")
            self.tasmota.stop()

if __name__ == '__main__':
    unittest.main()
