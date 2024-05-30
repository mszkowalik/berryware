from adapters.tasmota_adapter import TasmotaAdapter
from time import sleep

def main():
    # Create multiple instances of TasmotaAdapter with unique EUI identifiers
    tasmota = TasmotaAdapter("EUI53EF3GD1")


    # Start each TasmotaAdapter instance
    tasmota.start()
    sleep(10)
    tasmota.stop()

if __name__ == "__main__":
    main()
