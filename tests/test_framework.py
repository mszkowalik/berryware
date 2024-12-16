import threading
import time
import os
import pytest
from adapters.tasmota_adapter import TasmotaAdapter


@pytest.fixture
def tasmota_setup():
    # Create an instance of TasmotaAdapter with a unique EUI
    tasmota = TasmotaAdapter("EUI_TEST")

    # Path to the test autoexec file
    autoexec_path = os.path.join(os.path.dirname(__file__), "test_autoexec.py")

    # Create a custom driver for testing
    class CustomDriver:
        def __init__(self):
            self.counter_250ms = 0

        def every_250ms(self):
            self.counter_250ms += 1
            print(f"every_250ms called {self.counter_250ms} times")

        def every_second(self):
            print("every_second called")

    driver = CustomDriver()
    tasmota.add_driver(driver)

    # Function to run tasmota
    def run_tasmota():
        tasmota.start(autoexec_path=autoexec_path)

    # Start the TasmotaAdapter instance in a separate thread
    autoexec_thread = threading.Thread(target=run_tasmota)
    autoexec_thread.daemon = True  # Allows thread to be killed when main thread exits

    # Function to run autoexec for a certain duration
    def run_autoexec_for_duration(duration):
        autoexec_thread.start()
        time.sleep(duration)
        print("Stopping autoexec after duration")
        # Stopping autoexec by stopping the TasmotaAdapter instance
        tasmota.stop()
        autoexec_thread.join()

    yield tasmota, driver, run_autoexec_for_duration

    # Cleanup after test
    if autoexec_thread.is_alive():
        print("Terminating autoexec thread")
        tasmota.stop()
        autoexec_thread.join()


def test_run_autoexec(tasmota_setup):
    tasmota, driver, run_autoexec_for_duration = tasmota_setup

    # Run autoexec for a specified duration and simulate device operations
    run_autoexec_for_duration(0.5)  # Run for 0.5 seconds

    # Check that the driver's `every_250ms` method was called
    assert driver.counter_250ms > 0, "Driver's every_250ms should have been called"
