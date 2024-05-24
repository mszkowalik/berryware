import threading

class Tasmota:
    def cmd(self, command):
        print(f"Tasmota Command: {command}")

    def set_timer(self, timeout, callback, timer_name):
        print(f"Timer {timer_name} set for {timeout} ms")
        threading.Timer(timeout / 1000, callback).start()

    def remove_timer(self, timer_name):
        print(f"Timer {timer_name} removed")

    def time_str(self, rtc):
        return "2024-05-24T12:34:56"

    def rtc(self):
        return {"local": "local_time"}

    def web_send(self, message):
        print(f"Web Message: {message}")

    def add_rule(self, event, action, rule_id):
        print(f"Added rule {rule_id} for event {event}")

    def add_driver(self, driver):
        print(f"Added driver {driver}")

tasmota = Tasmota()
