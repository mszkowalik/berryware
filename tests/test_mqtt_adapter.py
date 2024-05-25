import unittest
from mqtt_adapter import MQTTAdapter

class TestMQTTAdapter(unittest.TestCase):
    def setUp(self):
        self.mqtt = MQTTAdapter()
        self.mqtt.subscriptions = {}  # Reset subscriptions before each test

    def test_subscribe_and_publish(self):
        messages = []

        def callback(topic, message):
            messages.append((topic, message))

        self.mqtt.subscribe("test/topic", callback)
        self.mqtt.publish("test/topic", "Hello, world!")

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], ("test/topic", "Hello, world!"))

    def test_unsubscribe(self):
        messages = []

        def callback(topic, message):
            messages.append((topic, message))

        self.mqtt.subscribe("test/topic", callback)
        self.mqtt.unsubscribe("test/topic", callback)
        self.mqtt.publish("test/topic", "Hello, world!")

        self.assertEqual(len(messages), 0)

    def test_publish_without_subscription(self):
        messages = []

        def callback(topic, message):
            messages.append((topic, message))

        self.mqtt.publish("test/topic", "Hello, world!")
        self.assertEqual(len(messages), 0)

    def test_multiple_callbacks(self):
        messages1 = []
        messages2 = []

        def callback1(topic, message):
            messages1.append((topic, message))

        def callback2(topic, message):
            messages2.append((topic, message))

        self.mqtt.subscribe("test/topic", callback1)
        self.mqtt.subscribe("test/topic", callback2)
        self.mqtt.publish("test/topic", "Hello, world!")

        self.assertEqual(len(messages1), 1)
        self.assertEqual(messages1[0], ("test/topic", "Hello, world!"))

        self.assertEqual(len(messages2), 1)
        self.assertEqual(messages2[0], ("test/topic", "Hello, world!"))

    def test_unsubscribe_single_callback(self):
        messages1 = []
        messages2 = []

        def callback1(topic, message):
            messages1.append((topic, message))

        def callback2(topic, message):
            messages2.append((topic, message))

        self.mqtt.subscribe("test/topic", callback1)
        self.mqtt.subscribe("test/topic", callback2)
        self.mqtt.unsubscribe("test/topic", callback1)
        self.mqtt.publish("test/topic", "Hello, world!")

        self.assertEqual(len(messages1), 0)
        self.assertEqual(len(messages2), 1)
        self.assertEqual(messages2[0], ("test/topic", "Hello, world!"))

if __name__ == '__main__':
    unittest.main()
