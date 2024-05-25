import threading
from adapters.mqtt_adapter import MQTTAdapter
from adapters.singleton import singleton
import json

@singleton
class TasmotaAdapter:
    def __init__(self, EUI):
        self.EUI = EUI
        self.devices = []
        self.mqtt = MQTTAdapter()

    def add_device(self, device):
        self.devices.append(device)

    def cmd(self, command):
        print(f"Executing Tasmota command: {command}")
        if isinstance(command, str) and command == "status5":
            return {"Status": {"Topic": "dummy_topic"}}
        elif isinstance(command, dict) and "ModBusSend" in command:
            modbus_cmd = command["ModBusSend"]
            device_address = modbus_cmd["deviceaddress"]
            function_code = modbus_cmd["functioncode"]
            start_address = modbus_cmd["startaddress"]
            count = modbus_cmd["count"]

            for device in self.devices:
                response = device.get_response(device_address, function_code, start_address, count)
                if response:
                    self.mqtt.publish(f"tele/{self.EUI}/ModbusReceived", json.dumps(response))
                    return response
        return {}

    def set_timer(self, delay, callback, timer_name=None):
        def timer_callback():
            threading.Timer(delay / 1000, callback).start()

        timer_callback()
