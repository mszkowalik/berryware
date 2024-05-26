import json
import threading
import random

class ModbusBridge:
    def __init__(self, tasmota_adapter):
        self.tasmota_adapter = tasmota_adapter
        self.register_commands()

    def register_commands(self):
        self.tasmota_adapter.register_command("ModBusSend", self.handle_modbus_send)
        self.tasmota_adapter.register_command("ModBusSetBaudrate", self.handle_set_baudrate)
        self.tasmota_adapter.register_command("ModBusSetConfig", self.handle_set_config)

    def handle_modbus_send(self, command_payload):
        try:
            modbus_send = json.loads(command_payload)
            device_address = modbus_send.get("deviceaddress")
            function_code = modbus_send.get("functioncode")
            start_address = modbus_send.get("startaddress")
            count = modbus_send.get("count")
            type = modbus_send.get("type", "uint16")

            # Immediate response
            result = {"ModbusSend": "Done"}
            self.tasmota_adapter.publish_result(result, 'RESULT', 'stat')

            # Simulate delayed device response
            delay = random.uniform(0.05, 0.15)
            threading.Timer(delay, self._send_modbus_response, args=(device_address, function_code, start_address, count, type)).start()

            return result
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format"}

    def _send_modbus_response(self, device_address, function_code, start_address, count, type):
        for device in self.tasmota_adapter.devices:
            response = device.get_response(device_address, function_code, start_address, count)
            if response:
                response["type"] = type
                full_response = {"ModbusReceived": response}
                response_json = json.dumps(full_response)
                self.tasmota_adapter.cmd_logger.debug(f'RESULT = {response_json}')
                self.tasmota_adapter.publish_result(response_json, 'RESULT', 'tele')
                break

    def handle_set_baudrate(self, command_payload):
        try:
            baudrate = int(command_payload)
            if 1200 <= baudrate <= 115200:
                self.tasmota_adapter.baudrate = baudrate
                result = {"Baudrate": baudrate}
                self.tasmota_adapter.publish_result(result, 'RESULT', 'stat')
                return result
            return {"error": "Invalid baudrate"}
        except ValueError:
            return {"error": "Invalid baudrate format"}


    def handle_set_config(self, command_payload):
        try:
            config = int(command_payload)
            valid_configs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            if config in valid_configs:
                self.tasmota_adapter.serial_config = config
                result = {"SerialConfig": config}
                self.tasmota_adapter.publish_result(result, 'RESULT', 'stat')
                return result
            return {"error": "Invalid serial config"}
        except ValueError:
            return {"error": "Invalid serial config format"}
