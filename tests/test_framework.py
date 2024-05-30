import unittest
import threading
import time
import os
from adapters.tasmota_adapter import TasmotaAdapter

class TestAutoexec(unittest.TestCase):
    def setUp(self):
        # Create an instance of TasmotaAdapter with a unique EUI
        self.tasmota = TasmotaAdapter("EUI_TEST")

        # Path to the test autoexec file
        self.autoexec_path = os.path.join(os.path.dirname(__file__), 'test_autoexec.py')

        # Create a custom driver for testing
        class CustomDriver:
            def __init__(self):
                self.counter_250ms = 0

            def every_250ms(self):
                self.counter_250ms += 1
                print(f"every_250ms called {self.counter_250ms} times")

            def every_second(self):
                print("every_second called")

        self.driver = CustomDriver()
        self.tasmota.add_driver(self.driver)

        # Start the TasmotaAdapter instance in a separate thread
        self.autoexec_thread = threading.Thread(target=self.run_tasmota)
        self.autoexec_thread.daemon = True  # Allows thread to be killed when main thread exits

    def run_tasmota(self):
        self.tasmota.start(autoexec_path=self.autoexec_path)

    def run_autoexec_for_duration(self, duration):
        self.autoexec_thread.start()
        time.sleep(duration)
        print("Stopping autoexec after duration")
        # Stopping autoexec by stopping the TasmotaAdapter instance
        self.tasmota.stop()

    def test_run_autoexec(self):
        # Run autoexec for a specified duration and simulate device operations
        self.run_autoexec_for_duration(1)  # Run for 1 seconds

        # Check that the driver `every_250ms` method was called
        self.assertTrue(self.driver.counter_250ms > 0, "Driver's every_250ms should have been called")

    def tearDown(self):
        # Cleanup code after each test
        if self.autoexec_thread.is_alive():
            print("Terminating autoexec thread")
            self.tasmota.stop()

if __name__ == '__main__':
    unittest.main()
