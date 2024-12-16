import threading
import time
import pytest
from adapters.tasmota_adapter import TasmotaAdapter
from custom_driver import CustomDriver


@pytest.fixture
def tasmota_driver():
    # Initialize the TasmotaAdapter and register the CustomDriver
    tasmota = TasmotaAdapter("EUI53EF3GD")
    driver = CustomDriver()
    tasmota.add_driver(driver)
    autoexec_thread = threading.Thread(target=tasmota.start)
    autoexec_thread.daemon = True  # Allows thread to be killed when main thread exits

    def run_autoexec_for_duration(duration):
        autoexec_thread.start()
        time.sleep(duration)
        print("Stopping TasmotaAdapter after duration")
        # Stopping TasmotaAdapter
        tasmota.stop()
        autoexec_thread.join()

    yield tasmota, driver, run_autoexec_for_duration

    # Cleanup after tests
    if autoexec_thread.is_alive():
        print("Terminating autoexec thread")
        tasmota.stop()
        autoexec_thread.join()


def test_run_custom_driver(tasmota_driver):
    tasmota, driver, run_autoexec_for_duration = tasmota_driver

    # Run TasmotaAdapter for a specified duration and simulate device operations
    run_autoexec_for_duration(1.1)  # Run for 1.1 seconds

    # Check that the driver's methods were called
    assert driver.counter_50ms > 0, "Driver's every_50ms should have been called"
    assert driver.counter_100ms > 0, "Driver's every_100ms should have been called"
    assert driver.counter_250ms > 0, "Driver's every_250ms should have been called"
    assert driver.counter_second > 0, "Driver's every_second should have been called"


def test_button_pressed(tasmota_driver):
    tasmota, driver, _ = tasmota_driver
    tasmota.button_pressed()
    assert driver.button_press_count == 1, "Driver's button_pressed should have been called once"


def test_mqtt_data(tasmota_driver):
    tasmota, driver, _ = tasmota_driver
    topic = "test/topic"
    message = "test message"
    tasmota.mqtt.publish(topic, message)
    time.sleep(0.1)  # Ensure the message is processed
    assert (topic, message) in driver.mqtt_messages, "Driver's mqtt_data should have received the message"


def test_save_before_restart(tasmota_driver):
    tasmota, driver, _ = tasmota_driver
    tasmota.stop()
    assert driver.save_before_restart_called, "Driver's save_before_restart should have been called"
