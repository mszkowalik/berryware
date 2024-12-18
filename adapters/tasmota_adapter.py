import threading
import json
import os
import requests
import logging
from .mqtt_adapter import MQTTAdapter
from .persist_adapter import PersistAdapter
from .modules.modbus_bridge import ModbusBridge

from .file_redirect import custom_open
from .basic_lib import (
    JSONModule as custom_json,
    MathModule as custom_math,
    TimeModule as custom_time,
    List,
    Map,
    Range,
    Bytes,
    custom_print,
    classname,
    custom_input,
    custom_str,
    number,
    custom_int,
    real,
    custom_bool,
    custom_type,
    custom_size,
    custom_super,
    custom_assert,
    custom_compile,
)


class TasmotaAdapter:
    def __init__(self, EUI):
        self.EUI = EUI
        self.devices = []
        self.mqtt = MQTTAdapter()
        self.persist = PersistAdapter()
        self.heap = 1024 * 64  # Example heap size
        self.rules = {}
        self.drivers = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self.cmd_logger = logging.getLogger("command_line")
        self.cmd_logger.setLevel(logging.DEBUG)
        self.running = False
        self.commands = {}
        self.current_command = None

        # Create the filesystem directory if it doesn't exist
        if not os.path.exists("./filesystem"):
            os.makedirs("./filesystem")

        # Subscribe to all MQTT messages
        self.mqtt.subscribe("#", self.handle_mqtt_message)

        # Initialize command modules
        self.command_modules = {"ModbusBridge": ModbusBridge(self)}

    def handle_mqtt_message(self, topic, message):
        for driver in self.drivers:
            if hasattr(driver, "mqtt_data"):
                driver.mqtt_data(topic, 0, message, len(message))

    def register_command(self, command_name, handler):
        self.commands[command_name] = handler

    def add_device(self, device):
        self.devices.append(device)
        self.logger.debug(f"Device added: {device}")

    def get_free_heap(self):
        return self.heap

    def publish_result(self, result_dict: dict, subtopic: str, prefix: str = "tele"):
        payload = json.dumps(result_dict)
        topic = f"{prefix}/{self.EUI}/{subtopic}"
        self.mqtt.publish(topic, payload)
        self.cmd_logger.debug(f"RESULT = {payload}")

    def publish_rule(self, payload: str) -> bool:
        self.cmd_logger.debug(f"Published rule with payload: {payload}")
        return True

    def cmd(self, command_str, mute: bool = False):
        self.cmd_logger.debug(f"Executing Tasmota command: {command_str}")
        response = None
        try:
            command_name, command_payload = command_str.split(" ", 1)
            if command_name in self.commands:
                self.current_command = command_name
                handler = self.commands[command_name]
                result = handler(command_payload)
                if not mute and result is not None:
                    result_str = ""
                    if isinstance(result, dict):
                        result_str = json.dumps(result)
                    else:
                        result_str = result
                    response = self.resp_cmnd(result_str)
        except Exception as e:
            self.logger.error(f"Error executing command {command_str}: {e}")

        self.current_command = None
        return response

    def resp_cmnd(self, message: str):
        """Send a custom JSON message as a command response."""
        response = (
            {self.current_command: message} if self.current_command else {"Command": "Unknown"}
        )
        self.publish_result(response, "RESULT", prefix="stat")
        return response

    def resp_cmnd_done(self):
        """Report command as Done."""
        response = "Done"
        self.resp_cmnd(json.dumps(response))

    def resp_cmnd_error(self):
        """Report command as Error."""
        response = "Error"
        self.resp_cmnd(json.dumps(response))

    def resp_cmnd_failed(self):
        """Report command as Failed."""
        response = "Failed"
        self.resp_cmnd(json.dumps(response))

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
                self.rules[trigger] = [rule for rule in self.rules[trigger] if rule["id"] != id]
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

    def stop(self):
        self.logger.debug("Stopping TasmotaAdapter")
        for driver in self.drivers:
            if hasattr(driver, "save_before_restart"):
                driver.save_before_restart()
        self.running = False
        self.persist.save()

    def run_periodic_callbacks(self):
        if not self.running:
            return

        def every_50ms():
            for driver in self.drivers:
                if hasattr(driver, "every_50ms"):
                    driver.every_50ms()
            self.set_timer(50, every_50ms)

        def every_100ms():
            for driver in self.drivers:
                if hasattr(driver, "every_100ms"):
                    driver.every_100ms()
            self.set_timer(100, every_100ms)

        def every_250ms():
            for driver in self.drivers:
                if hasattr(driver, "every_250ms"):
                    driver.every_250ms()
            self.set_timer(250, every_250ms)

        def every_second():
            for driver in self.drivers:
                if hasattr(driver, "every_second"):
                    driver.every_second()
            self.set_timer(1000, every_second)

        every_50ms()
        every_100ms()
        every_250ms()
        every_second()

    def button_pressed(self):
        for driver in self.drivers:
            if hasattr(driver, "button_pressed"):
                driver.button_pressed()

    def run_autoexec(self, autoexec_path=None):
        if autoexec_path is None:
            autoexec_path = os.path.join(os.path.dirname(__file__), "..", "autoexec", "autoexec.py")
        if os.path.exists(autoexec_path):
            with open(autoexec_path, "rb") as source_file:
                code = compile(source_file.read(), autoexec_path, "exec")
                # Execute the code with the required context
                exec(
                    code,
                    {
                        "tasmota": self,
                        "mqtt": self.mqtt,
                        "persist": self.persist,
                        "open": custom_open,
                        "json": custom_json,
                        "math": custom_math,
                        "time": custom_time,
                        "List": List,
                        "Map": Map,
                        "Range": Range,
                        "Bytes": Bytes,
                        "print": custom_print,
                        "classname": classname,
                        "input": custom_input,
                        "str": custom_str,
                        "number": number,
                        "int": custom_int,
                        "real": real,
                        "bool": custom_bool,
                        "type": custom_type,
                        "size": custom_size,
                        "super": custom_super,
                        "assert_": custom_assert,
                        "compile": custom_compile,
                    },
                )

    def start(self, autoexec_path=None):
        self.running = True
        self.logger.debug("Starting TasmotaAdapter")
        self.run_periodic_callbacks()
        self.run_autoexec(autoexec_path=autoexec_path)


# Usage example
if __name__ == "__main__":
    tasmota_adapter = TasmotaAdapter("EUI53EF3GD")
    tasmota_adapter.start()
