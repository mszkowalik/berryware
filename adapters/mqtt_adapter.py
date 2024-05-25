from adapters.singleton import singleton

@singleton
class MQTTAdapter:
    def __init__(self):
        self.subscriptions = {}

    def subscribe(self, topic, callback):
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        self.subscriptions[topic].append(callback)

    def publish(self, topic, message):
        if topic in self.subscriptions:
            for callback in self.subscriptions[topic]:
                callback(topic, message)

    def unsubscribe(self, topic, callback=None):
        if topic in self.subscriptions:
            if callback:
                if callback in self.subscriptions[topic]:
                    self.subscriptions[topic].remove(callback)
                if not self.subscriptions[topic]:
                    del self.subscriptions[topic]
            else:
                del self.subscriptions[topic]

mqtt = MQTTAdapter()