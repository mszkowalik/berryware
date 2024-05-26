class CustomDriver:
    def __init__(self):
        self.counter_50ms = 0
        self.counter_100ms = 0
        self.counter_250ms = 0
        self.counter_second = 0
        self.button_press_count = 0
        self.mqtt_messages = []
        self.save_before_restart_called = False

    def every_50ms(self):
        self.counter_50ms += 1
        print(f"every_50ms called {self.counter_50ms} times")

    def every_100ms(self):
        self.counter_100ms += 1
        print(f"every_100ms called {self.counter_100ms} times")

    def every_250ms(self):
        self.counter_250ms += 1
        print(f"every_250ms called {self.counter_250ms} times")

    def every_second(self):
        self.counter_second += 1
        print(f"every_second called {self.counter_second} times")

    def button_pressed(self):
        self.button_press_count += 1
        print(f"button_pressed called {self.button_press_count} times")

    def mqtt_data(self, topic, idx, data, databytes):
        self.mqtt_messages.append((topic, data))
        print(f"mqtt_data received message on {topic}: {data}")

    def save_before_restart(self):
        self.save_before_restart_called = True
        print("save_before_restart called")

    def set_power_handler(self, cmd, idx):
        print(f"set_power_handler called with cmd: {cmd}, idx: {idx}")
