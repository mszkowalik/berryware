from .mqtt_adapter import MQTTAdapter
from .tasmota_adapter import TasmotaAdapter

mqtt = MQTTAdapter()
tasmota = TasmotaAdapter("EUI53EF3GD")
