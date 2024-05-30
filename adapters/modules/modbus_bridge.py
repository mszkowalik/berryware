import json
import threading
import random

class ModbusBridge:
    def __init__(self, tasmota_adapter):
        self.tasmota_adapter = tasmota_adapter
        self.serial_config = 0
        self.baudrate = 9600
        self.register_commands()

    def register_commands(self):
        self.tasmota_adapter.register_command("ModbusSend", self.handle_modbus_send)
        self.tasmota_adapter.register_command("ModbusBaudrate", self.handle_set_baudrate)
        self.tasmota_adapter.register_command("ModbusConfig", self.handle_set_config)

    def handle_modbus_send(self, command_payload):

        modbus_send = json.loads(command_payload)
        device_address = modbus_send.get("deviceaddress")
        function_code = modbus_send.get("functioncode")
        start_address = modbus_send.get("startaddress")
        count = modbus_send.get("count")
        type = modbus_send.get("type", "uint16")


        # Simulate delayed device response
        delay = random.uniform(0.05, 0.15)
        threading.Timer(delay, self._send_modbus_response, args=(device_address, function_code, start_address, count, type)).start()

        # Immediate response
        self.tasmota_adapter.resp_cmnd_done()


    def _send_modbus_response(self, device_address, function_code, start_address, count, type):
        for device in self.tasmota_adapter.devices:
            response = device.get_response(device_address, function_code, start_address, count)
            if response:
                response["type"] = type
                full_response = {"ModbusReceived": response}
                self.tasmota_adapter.cmd_logger.debug(f'RESULT = {json.dumps(full_response)}')
                self.tasmota_adapter.publish_result(full_response, 'RESULT', 'tele')
                break

    def handle_set_baudrate(self, command_payload):
        baudrate = int(command_payload)
        if 1200 <= baudrate <= 115200:
            self.baudrate = baudrate
        return self.baudrate

    def handle_set_config(self, command_payload):
        config = int(command_payload)
        valid_configs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        if config in valid_configs:
            self.serial_config = config
        return self.serial_config
