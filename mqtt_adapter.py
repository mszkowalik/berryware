class MQTTAdapter:
    def __init__(self):
        self.subscriptions = {}

    def subscribe(self, topic, callback):
        self.subscriptions[topic] = callback

    def unsubscribe(self, topic):
        if topic in self.subscriptions:
            del self.subscriptions[topic]

    def publish(self, topic, message):
        if topic in self.subscriptions:
            self.subscriptions[topic](topic, message)

mqtt = MQTTAdapter()
