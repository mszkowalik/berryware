from adapters.tasmota_adapter import TasmotaAdapter
from adapters.persist_adapter import PersistAdapter
from time import sleep

def main():
    # Create multiple instances of TasmotaAdapter with unique EUI identifiers
    tasmota = TasmotaAdapter("EUI53EF3GD1")
    tasmota.persist = PersistAdapter("./filesystem/_persist.json")


    # Start each TasmotaAdapter instance
    tasmota.persist.zero()
    tasmota.persist.save()
    tasmota.start()
    sleep(10)
    tasmota.stop()

if __name__ == "__main__":
    main()
