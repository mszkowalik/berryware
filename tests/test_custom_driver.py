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

        # Check that the driver's `every_250ms` and `every_second` methods were called
        self.assertTrue(self.driver.counter_250ms > 0, "Driver's every_250ms should have been called")
        self.assertTrue(self.driver.counter_second > 0, "Driver's every_second should have been called")

    def tearDown(self):
        # Cleanup code after each test
        if self.autoexec_thread.is_alive():
            print("Terminating autoexec thread")
            self.tasmota.stop()

if __name__ == '__main__':
    unittest.main()
