import unittest
from mqtt_adapter import mqtt
from tasmota_adapter import tasmota

class TestClass:
    def __init__(self):
        self.json_response = {}
        self.received_messages = []
        self.collect_data = False

    def mqtt_set(self):
        mqtt.subscribe('ITERATOR_TEST', self.mqtt_data)
        mqtt.subscribe('CONFIG', self.mqtt_data)
        mqtt.subscribe('INTERVAL', self.mqtt_data)
        mqtt.subscribe('ModbusSend', self.mqtt_data)

    def mqtt_unset(self):
        mqtt.unsubscribe('ITERATOR_TEST')
        mqtt.unsubscribe('CONFIG')
        mqtt.unsubscribe('INTERVAL')
        mqtt.unsubscribe('ModbusSend')

    def mqtt_data(self, topic, message):
        print(f"Received message on topic {topic}: {message}")
        self.received_messages.append((topic, message))
        if topic == 'ITERATOR_TEST':
            if message == '1':
                self.start_over()
            elif message == '0':
                self.stop()
        # Add more handling as needed

    def start_over(self):
        print("Monitoring awaking")
        self.clear_response()
        self.collect_data = True

    def stop(self):
        print("Monitoring stop")
        self.collect_data = False

    def clear_response(self):
        for key in self.json_response:
            self.json_response[key] = "-"

    def tasmota_command(self, command):
        return tasmota.cmd(command)

    def set_tasmota_timer(self, delay, callback):
        tasmota.set_timer(delay, callback)


class TestMQTTAndTasmota(unittest.TestCase):
    def setUp(self):
        self.test_instance = TestClass()
        self.test_instance.mqtt_set()

    def tearDown(self):
        self.test_instance.mqtt_unset()

    def test_mqtt_subscribe_and_publish(self):
        mqtt.publish('ITERATOR_TEST', '1')
        self.assertIn(('ITERATOR_TEST', '1'), self.test_instance.received_messages)

    def test_tasmota_cmd(self):
        response = self.test_instance.tasmota_command('status5')
        self.assertEqual(response, {"Status": {"Topic": "dummy_topic"}})

    def test_tasmota_set_timer(self):
        def callback():
            self.test_instance.json_response['timer'] = 'Booh!'
        self.test_instance.set_tasmota_timer(50, callback)
        # Sleep to wait for the timer to trigger
        import time
        time.sleep(0.06)
        self.assertEqual(self.test_instance.json_response['timer'], 'Booh!')

if __name__ == "__main__":
    unittest.main()
