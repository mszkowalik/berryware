from adapters import tasmota

class MyDriver:
    def __init__(self):
        self.counter = 0

    def every_250ms(self):
        self.counter += 1
        print(f"every_250ms called {self.counter} times")

    def every_second(self):
        print("every_second called")

def main():
    driver = MyDriver()
    tasmota.add_driver(driver)
    print("Driver added to Tasmota")

if __name__ == "__main__":
    main()
