import unittest
from adapters.mqtt_adapter import MQTTAdapter

class TestMQTTAdapter(unittest.TestCase):
    def setUp(self):
        self.mqtt = MQTTAdapter()
        self.received_messages = []

    def on_message(self, topic, message):
        self.received_messages.append((topic, message))

    def test_exact_topic_subscription(self):
        topic = "test/topic"
        message = "test message"

        self.mqtt.subscribe(topic, self.on_message)
        self.mqtt.publish(topic, message)

        self.assertIn((topic, message), self.received_messages)

    def test_single_level_wildcard_subscription(self):
        topic = "test/+/subtopic"
        message = "test message"

        self.mqtt.subscribe(topic, self.on_message)
        self.mqtt.publish("test/one/subtopic", message)
        self.mqtt.publish("test/two/subtopic", message)

        self.assertIn(("test/one/subtopic", message), self.received_messages)
        self.assertIn(("test/two/subtopic", message), self.received_messages)

    def test_multilevel_wildcard_subscription(self):
        topic = "test/#"
        message = "test message"

        self.mqtt.subscribe(topic, self.on_message)
        self.mqtt.publish("test/one/two/three", message)
        self.mqtt.publish("test/one/two", message)
        self.mqtt.publish("test/one", message)

        self.assertIn(("test/one/two/three", message), self.received_messages)
        self.assertIn(("test/one/two", message), self.received_messages)
        self.assertIn(("test/one", message), self.received_messages)

    def test_mixed_wildcard_subscription(self):
        topic = "test/+/subtopic/#"
        message = "test message"

        self.mqtt.subscribe(topic, self.on_message)
        self.mqtt.publish("test/one/subtopic/level1", message)
        self.mqtt.publish("test/two/subtopic/level1/level2", message)

        self.assertIn(("test/one/subtopic/level1", message), self.received_messages)
        self.assertIn(("test/two/subtopic/level1/level2", message), self.received_messages)

    def test_no_match_subscription(self):
        topic = "test/+/subtopic"
        message = "test message"

        self.mqtt.subscribe(topic, self.on_message)
        self.mqtt.publish("test/one/another", message)
        self.mqtt.publish("another/test/subtopic", message)

        self.assertNotIn(("test/one/another", message), self.received_messages)
        self.assertNotIn(("another/test/subtopic", message), self.received_messages)

    def tearDown(self):
        self.mqtt.reset()
        self.received_messages = []

if __name__ == '__main__':
    unittest.main()
