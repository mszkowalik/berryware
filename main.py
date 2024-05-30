from adapters.tasmota_adapter import TasmotaAdapter
from time import sleep

def main():
    # Create multiple instances of TasmotaAdapter with unique EUI identifiers
    tasmota_adapter1 = TasmotaAdapter("EUI53EF3GD1")
    tasmota_adapter2 = TasmotaAdapter("EUI53EF3GD2")

    # Start each TasmotaAdapter instance
    tasmota_adapter1.start()
    tasmota_adapter2.start()
    sleep(10)
    tasmota_adapter1.stop()
    tasmota_adapter2.stop()

if __name__ == "__main__":
    main()
