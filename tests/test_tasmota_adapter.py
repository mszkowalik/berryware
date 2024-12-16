import pytest
import os
import shutil
import time
import requests
from adapters.tasmota_adapter import TasmotaAdapter
from adapters.modbus_device import ModbusDevice


@pytest.fixture
def tasmota_adapter():
    tasmota = TasmotaAdapter("EUI53EF3GD")
    mqtt = tasmota.mqtt
    device = ModbusDevice(
        "TestDevice",
        "TestManufacturer",
        "TestPartNumber",
        {
            "33049": {
                "name": "PV-V-A",
                "functioncode": 4,
                "type": "uint16",
                "count": 1,
                "sum": 10,
            },
        },
    )
    tasmota.add_device(device)
    received_messages = []

    def on_message(topic, message):
        received_messages.append((topic, message))

    mqtt.subscribe("#", on_message)

    # Create filesystem directory if it doesn't exist
    if not os.path.exists("filesystem"):
        os.makedirs("filesystem")

    yield tasmota, mqtt, device, received_messages

    # Cleanup after tests
    if os.path.exists("filesystem"):
        shutil.rmtree("filesystem")


def test_set_device_working(tasmota_adapter):
    tasmota, mqtt, device, received_messages = tasmota_adapter
    device.set_working(False)
    command = 'ModbusSend {"deviceaddress": 2, "functioncode": 4, "startaddress": 33049, "count": 1}'

    tasmota.cmd(command)
    assert len(received_messages) == 1
    topic, message = received_messages[-1]
    assert topic == f"stat/{tasmota.EUI}/RESULT"
    assert "ModbusSend" in message


def test_error_rate(tasmota_adapter):
    tasmota, mqtt, device, received_messages = tasmota_adapter
    error_rate = 0.5
    device.set_error_rate(error_rate)
    command = 'ModbusSend {"deviceaddress": 2, "functioncode": 4, "startaddress": 33049, "count": 1}'

    success_count = 0
    attempts = 1000

    def on_message(topic, message):
        nonlocal success_count
        if topic == f"tele/{tasmota.EUI}/RESULT" and "ModbusReceived" in message:
            success_count += 1

    mqtt.subscribe(f"tele/{tasmota.EUI}/RESULT", on_message)

    for _ in range(attempts):
        tasmota.cmd(command)

    time.sleep(0.15)  # Wait for all modbus responses
    observed_error_rate = 1 - (success_count / attempts)
    assert abs(observed_error_rate - error_rate) <= 0.05


def test_urlfetch(tasmota_adapter, monkeypatch):
    tasmota, _, _, _ = tasmota_adapter

    def mock_get(url, stream=True):
        class MockResponse:
            def iter_content(self, chunk_size=1):
                yield b"test data"

            def raise_for_status(self):
                pass

        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)

    url = "http://example.com/testfile"
    filename = "testfile"
    expected_file_path = os.path.join("filesystem", filename)

    bytes_downloaded = tasmota.urlfetch(url)

    assert bytes_downloaded == len(b"test data")
    assert os.path.exists(expected_file_path)

    with open(expected_file_path, "rb") as f:
        assert f.read() == b"test data"


def test_add_rule(tasmota_adapter):
    tasmota, _, _, _ = tasmota_adapter

    def dummy_rule(cmd, idx, payload, raw):
        pass

    tasmota.add_rule("test_trigger", dummy_rule, id="test_rule")
    assert "test_trigger" in tasmota.rules
    assert len(tasmota.rules["test_trigger"]) == 1
    assert tasmota.rules["test_trigger"][0]["id"] == "test_rule"


def test_remove_rule(tasmota_adapter):
    tasmota, _, _, _ = tasmota_adapter

    def dummy_rule(cmd, idx, payload, raw):
        pass

    tasmota.add_rule("test_trigger", dummy_rule, id="test_rule")
    tasmota.remove_rule("test_trigger", id="test_rule")
    assert "test_trigger" not in tasmota.rules


def test_memory(tasmota_adapter):
    tasmota, _, _, _ = tasmota_adapter
    memory_stats = tasmota.memory()
    assert isinstance(memory_stats, dict)
    assert "iram_free" in memory_stats

    heap_free = tasmota.memory("heap_free")
    assert heap_free == 226


def test_gc(tasmota_adapter):
    tasmota, _, _, _ = tasmota_adapter
    allocated_bytes = tasmota.gc()
    assert allocated_bytes == tasmota.heap


def test_publish_result(tasmota_adapter):
    tasmota, mqtt, _, _ = tasmota_adapter
    payload = '{"status": "ok"}'
    subtopic = "status"
    received_messages = []

    def on_message(topic, message):
        received_messages.append((topic, message))

    topic = f"tele/{tasmota.EUI}/{subtopic}"

    mqtt.subscribe(topic, on_message)
    mqtt.publish(topic, payload)

    assert len(received_messages) == 1
    assert received_messages[0] == (topic, payload)


def test_publish_rule(tasmota_adapter):
    tasmota, _, _, _ = tasmota_adapter
    payload = '{"rule": "test"}'
    handled = tasmota.publish_rule(payload)
    assert handled


def test_modbus_send(tasmota_adapter):
    tasmota, mqtt, _, received_messages = tasmota_adapter
    command = 'ModbusSend {"deviceaddress": 2, "functioncode": 4, "startaddress": 33049, "count": 1}'

    tasmota.cmd(command)
    time.sleep(0.2)  # Wait for the delayed response
    assert len(received_messages) > 1
    topic, message = received_messages[-1]
    assert topic == f"tele/{tasmota.EUI}/RESULT"
    assert "ModbusReceived" in message


def test_modbus_set_baudrate(tasmota_adapter):
    tasmota, _, _, _ = tasmota_adapter
    command = "ModbusBaudrate 9600"

    response = tasmota.cmd(command)
    assert response == {"ModbusBaudrate": 9600}


def test_modbus_set_config(tasmota_adapter):
    tasmota, _, _, _ = tasmota_adapter
    command = "ModbusConfig 3"

    response = tasmota.cmd(command)
    assert response == {"ModbusConfig": 3}
