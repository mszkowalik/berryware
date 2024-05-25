import logging

class MQTTAdapter:
    def __init__(self):
        self.subscriptions = {}
        self.logger = logging.getLogger(self.__class__.__name__)

    def subscribe(self, topic, callback):
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        self.subscriptions[topic].append(callback)
        self.logger.debug(f"Subscribed to topic: {topic}")

    def publish(self, topic, message):
        if topic in self.subscriptions:
            for callback in self.subscriptions[topic]:
                callback(topic, message)
            self.logger.debug(f"Published message to topic: {topic}")
        self.logger.debug(f"No subscribers found for topic: {topic}")

    def unsubscribe(self, topic, callback=None):
        if topic in self.subscriptions:
            if callback:
                if callback in self.subscriptions[topic]:
                    self.subscriptions[topic].remove(callback)
                if not self.subscriptions[topic]:
                    del self.subscriptions[topic]
            else:
                del self.subscriptions[topic]
            self.logger.debug(f"Unsubscribed from topic: {topic}")
        self.logger.debug(f"Callback not found for topic: {topic}")

    def reset(self):
        self.subscriptions = {}
        self.logger.debug("Subscriptions reset")
