from .mqtt_adapter import MQTTAdapter
from .tasmota_adapter import TasmotaAdapter

tasmota = TasmotaAdapter("EUI53EF3GD")
mqtt = tasmota.mqtt
