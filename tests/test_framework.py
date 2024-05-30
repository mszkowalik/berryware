import unittest
import threading
import time
from adapters.tasmota_adapter import TasmotaAdapter

class TestAutoexec(unittest.TestCase):
    def setUp(self):
        # Create an instance of TasmotaAdapter with a unique EUI
        self.tasmota_adapter = TasmotaAdapter("EUI_TEST")

        # Start the TasmotaAdapter instance in a separate thread
        self.autoexec_thread = threading.Thread(target=self.run_tasmota)
        self.autoexec_thread.daemon = True  # Allows thread to be killed when main thread exits

    def run_tasmota(self):
        self.tasmota_adapter.start()

    def run_autoexec_for_duration(self, duration):
        self.autoexec_thread.start()
        time.sleep(duration)
        print("Stopping autoexec after duration")
        # Stopping autoexec by stopping the TasmotaAdapter instance
        self.tasmota_adapter.stop()

    def test_run_autoexec(self):
        # Run autoexec for a specified duration and simulate device operations
        self.run_autoexec_for_duration(5)  # Run for 5 seconds

        # Check that the driver `every_250ms` method was called
        driver = self.tasmota_adapter.drivers[0]
        self.assertTrue(driver.counter > 0, "Driver's every_250ms should have been called")

    def tearDown(self):
        # Cleanup code after each test
        if self.autoexec_thread.is_alive():
            print("Terminating autoexec thread")
            self.tasmota_adapter.stop()

if __name__ == '__main__':
    unittest.main()
