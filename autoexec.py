import mqtt_adapter as mqtt
import tasmota_adapter as tasmota

class iterator:
    def __init__(self, mqtt_topic_modbussend, mqtt_topic_monitoring, mqtt_topic_config, mqtt_topic_interval, device_address, interval, inverter, inverter_sn):
        self.EUI = "tasmota_cmd_status5"
        self.prefix = "tele/"
        self.address_map = {}
        self.device_address = device_address
        self.interval = interval
        self.inverter = inverter
        self.inverter_sn = inverter_sn
        self.json_response = {}

    def mqtt_set(self):
        mqtt.mqtt.subscribe(self.mqtt_topic_monitoring, self.mqtt_data)
        mqtt.mqtt.subscribe(self.mqtt_topic_config, self.mqtt_data)
        mqtt.mqtt.subscribe(self.mqtt_topic_interval, self.mqtt_data)
        mqtt.mqtt.subscribe(self.mqtt_topic_modbussend, self.mqtt_data)

    def mqtt_unset(self):
        mqtt.mqtt.unsubscribe(self.mqtt_topic_monitoring)
        mqtt.mqtt.unsubscribe(self.mqtt_topic_config)
        mqtt.mqtt.unsubscribe(self.mqtt_topic_interval)
        mqtt.mqtt.unsubscribe(self.mqtt_topic_modbussend)

    def mqtt_data(self, topic, message):
        if topic == self.mqtt_topic_monitoring:
            msg = message
            if msg == '1':
                self.start_over()
            elif msg == '0':
                self.stop()
        elif topic == self.mqtt_topic_config:
            pass  # Other logic

    def start_over(self):
        print("Monitoring awaking")
        self.clear_response()

    def stop(self):
        print("Monitoring stop")
        self.collect_data = False

    def clear_response(self):
        for key in self.json_response:
            self.json_response[key] = '-'

def main():
    iterator_instance = iterator("modbussend", "monitoring", "config", "interval", 1, 10, "SOLIS", "1234567890")
    iterator_instance.mqtt_set()

if __name__ == "__main__":
    main()
