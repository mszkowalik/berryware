## PYTHON SPECIFIC
from adapters import tasmota, mqtt
## PYTHON SPECIFIC

class Dongle:
    def __init__(self):
        self.counter = 0

    def every_250ms(self):
        self.counter += 1
        print(f"every_250ms called {self.counter} times")

    def every_second(self):
        print("every_second called")

## PYTHON SPECIFIC
def main():
    driver = Dongle()
    tasmota.add_driver(driver)
    print("Driver added to Tasmota")

if __name__ == "__main__":
    main()