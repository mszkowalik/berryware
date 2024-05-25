class CustomDriver:
    def __init__(self):
        self.counter_250ms = 0
        self.counter_second = 0

    def every_250ms(self):
        self.counter_250ms += 1
        print(f"every_250ms called {self.counter_250ms} times")

    def every_second(self):
        self.counter_second += 1
        print(f"every_second called {self.counter_second} times")
