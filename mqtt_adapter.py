class MQTT:
    def __init__(self):
        self.subscriptions = {}

    def subscribe(self, topic, callback):
        self.subscriptions[topic] = callback
        print(f"Subscribed to {topic}")

    def unsubscribe(self, topic):
        if topic in self.subscriptions:
            del self.subscriptions[topic]
            print(f"Unsubscribed from {topic}")

    def publish(self, topic, message):
        if topic in self.subscriptions:
            self.subscriptions[topic](topic, message)
        print(f"Published to {topic}: {message}")

mqtt = MQTT()
