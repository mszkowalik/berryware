# test_framework.py

import unittest
import threading
import time
import autoexec
from adapters import tasmota

class TestAutoexec(unittest.TestCase):
    def setUp(self):
        # Ensure the driver is added and tasmota instance is ready
        autoexec.main()
        self.autoexec_thread = threading.Thread(target=self.run_tasmota)
        self.autoexec_thread.daemon = True  # Allows thread to be killed when main thread exits

    def run_tasmota(self):
        tasmota.start()

    def run_autoexec_for_duration(self, duration):
        self.autoexec_thread.start()
        time.sleep(duration)
        print("Stopping autoexec after duration")
        # Stopping autoexec by simulating a KeyboardInterrupt
        tasmota.stop()

    def test_run_autoexec(self):
        # Run autoexec for a specified duration and simulate device operations
        self.run_autoexec_for_duration(5)  # Run for 5 seconds

        # Check that the driver `every_250ms` method was called
        driver = tasmota.drivers[0]
        self.assertTrue(driver.counter > 0, "Driver's every_250ms should have been called")

    def tearDown(self):
        # Cleanup code after each test
        if self.autoexec_thread.is_alive():
            print("Terminating autoexec thread")
            tasmota.stop()

if __name__ == '__main__':
    unittest.main()
