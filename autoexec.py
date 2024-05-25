import json
import time
from typing import List, Dict, Any
from adapters.mqtt_adapter import mqtt
from adapters.tasmota_adapter import tasmota
from adapters.persist import persist

# Predefined JSON dictionary of available registers
registers_json = {
    "SOLIS_4G": {
        "registers": [
            {"address": 3005, "name": "PV-Pf-value", "functioncode": 4, "type": "uint16", "count": 2, "scale": 1.0, "byteorder": "ABCD"},
            {"address": 3009, "name": "PV-Mr-d", "functioncode": 4, "type": "uint16", "count": 2, "scale": 1.0, "byteorder": "ABCD"},
            {"address": 3015, "name": "PV-Rd-value", "functioncode": 4, "type": "uint16", "count": 1, "scale": 1.0, "byteorder": "ABCD"},
            {"address": 3034, "name": "PV-V-A", "functioncode": 4, "type": "uint16", "count": 1, "scale": 1.0, "byteorder": "ABCD"},
            {"address": 3037, "name": "PV-A-A", "functioncode": 4, "type": "uint16", "count": 1, "scale": 1.0, "byteorder": "ABCD"},
            {"address": 3283, "name": "GR-Mr-c", "functioncode": 4, "type": "uint16", "count": 2, "scale": 1.0, "byteorder": "ABCD"},
            {"address": 3285, "name": "GR-Mr-d", "functioncode": 4, "type": "uint16", "count": 2, "scale": 1.0, "byteorder": "ABCD"}
        ],
        "requests": [
            {"deviceaddress": 1, "functioncode": 4, "startaddress": 3005, "type": "uint16", "count": 40, "interval": 60},
            {"deviceaddress": 1, "functioncode": 4, "startaddress": 3280, "type": "uint16", "count": 20, "interval": 60}
        ]
    }
}

# Configuration JSON for devices
config_json = {
    "devices": [
        {"name": "Inverter 1", "type": "SOLIS_4G", "address": 1}
    ]
}

# Driver class that generates Modbus requests
class MyDriver:
    def __init__(self, devices: List[Dict[str, Any]], registers: Dict[str, Any]):
        self.devices = devices
        self.registers = registers

    def every_second(self):
        print("Running every second task...")

    def every_250ms(self):
        print("Generating Modbus requests...")
        for device in self.devices:
            device_type = device["type"]
            if device_type in self.registers:
                for request in self.registers[device_type]["requests"]:
                    print(f"Generating Modbus request for device {device['name']} at address {request['startaddress']}")

