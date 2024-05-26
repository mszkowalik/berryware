import threading
import json
import os
import requests
import logging
from adapters.mqtt_adapter import MQTTAdapter


class TasmotaAdapter:
    def __init__(self, EUI):
        self.EUI = EUI
        self.devices = []
        self.mqtt = MQTTAdapter()
        self.heap = 1024 * 64  # Example heap size
        self.rules = {}
        self.drivers = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self.running = False

        # Create the filesystem directory if it doesn't exist
        if not os.path.exists("filesystem"):
            os.makedirs("filesystem")

        # Subscribe to all MQTT messages
        self.mqtt.subscribe("#", self.handle_mqtt_message)

    def handle_mqtt_message(self, topic, message):
        for driver in self.drivers:
            if hasattr(driver, "mqtt_data"):
                driver.mqtt_data(topic, 0, message, len(message))

    def add_device(self, device):
        self.devices.append(device)
        self.logger.debug(f"Device added: {device}")

    def get_free_heap(self):
        return self.heap

    def publish_result(self, payload: str, subtopic: str):
        self.mqtt.publish(f"tele/{self.EUI}/{subtopic}", payload)
        self.logger.debug(f"Published result to {subtopic} with payload: {payload}")

    def publish_rule(self, payload: str) -> bool:
        self.logger.debug(f"Published rule with payload: {payload}")
        return True

    def cmd(self, command, mute: bool = False):
        self.logger.debug(f"Executing Tasmota command: {command}")
        if isinstance(command, str) and command == "status5":
            return {"Status": {"Topic": "dummy_topic"}}
        elif isinstance(command, dict) and "ModBusSend" in command:
            modbus_cmd = command["ModBusSend"]
            device_address = modbus_cmd["deviceaddress"]
            function_code = modbus_cmd["functioncode"]
            start_address = modbus_cmd["startaddress"]
            count = modbus_cmd["count"]

            for device in self.devices:
                response = device.get_response(
                    device_address, function_code, start_address, count
                )
                if response:
                    self.mqtt.publish(
                        f"tele/{self.EUI}/ModbusReceived", json.dumps(response)
                    )
                    return response
        return {}

    def memory(self, key: str = None):
        mem_stats = {
            "iram_free": 41,
            "frag": 51,
            "program_free": 1856,
            "flash": 4096,
            "heap_free": 226,
            "program": 1679,
        }
        if key:
            return mem_stats.get(key)
        return mem_stats

    def add_rule(self, trigger: str, f, id: any = None):
        if trigger not in self.rules:
            self.rules[trigger] = []
        self.rules[trigger].append({"function": f, "id": id})
        self.logger.debug(f"Added rule with trigger: {trigger}")

    def remove_rule(self, trigger: str, id: any = None):
        if trigger in self.rules:
            if id is None:
                del self.rules[trigger]
                self.logger.debug(f"Removed all rules with trigger: {trigger}")
            else:
                self.rules[trigger] = [
                    rule for rule in self.rules[trigger] if rule["id"] != id
                ]
                if not self.rules[trigger]:
                    del self.rules[trigger]
                self.logger.debug(f"Removed rule with trigger: {trigger} and id: {id}")

    def add_driver(self, instance):
        self.drivers.append(instance)
        self.logger.debug(f"Driver added: {instance}")

    def remove_driver(self, instance):
        if instance in self.drivers:
            self.drivers.remove(instance)
            self.logger.debug(f"Driver removed: {instance}")

    def gc(self):
        self.logger.debug("Garbage collection triggered")
        return self.heap

    def urlfetch(self, url: str, filename: str = None) -> int:
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            if not filename:
                filename = os.path.basename(url)

            filepath = os.path.join("filesystem", filename)

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = os.path.getsize(filepath)
            self.logger.debug(
                f"Fetched URL: {url} and stored as {filename} with size {file_size} bytes"
            )
            return file_size
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch URL: {url} with error: {e}")
            return -1

    def urlbecload(self, url: str) -> bool:
        self.logger.debug(f"Loaded BEC file from URL: {url}")
        return True

    def set_timer(self, delay, callback, timer_name=None):
        def timer_callback():
            if self.running:
                threading.Timer(delay / 1000, callback).start()

        timer_callback()

    def start(self):
        self.running = True
        self.logger.debug("Starting TasmotaAdapter")
        self.run_periodic_callbacks()

    def stop(self):
        self.logger.debug("Stopping TasmotaAdapter")
        for driver in self.drivers:
            if hasattr(driver, "save_before_restart"):
                driver.save_before_restart()
        self.running = False

    def run_periodic_callbacks(self):
        if self.running:
            for driver in self.drivers:
                if hasattr(driver, "every_50ms"):
                    driver.every_50ms()
                if hasattr(driver, "every_100ms"):
                    driver.every_100ms()
                if hasattr(driver, "every_250ms"):
                    driver.every_250ms()
            self.set_timer(50, self.run_periodic_callbacks)
            for driver in self.drivers:
                if hasattr(driver, "every_second"):
                    driver.every_second()

    def button_pressed(self):
        for driver in self.drivers:
            if hasattr(driver, "button_pressed"):
                driver.button_pressed()


# Usage example
if __name__ == "__main__":
    tasmota_adapter = TasmotaAdapter("EUI53EF3GD")
    # Add your custom driver and other setup here
