import re
import fnmatch
import logging

class MQTTAdapter:
    def __init__(self):
        self.subscriptions = {}
        self.wildcard_subscriptions = {}

    def subscribe(self, topic, callback):
        if '#' in topic or '+' in topic:
            self.wildcard_subscriptions[topic] = callback
        else:
            if topic not in self.subscriptions:
                self.subscriptions[topic] = []
            self.subscriptions[topic].append(callback)

    def publish(self, topic, message):
        # Handle exact topic subscriptions
        if topic in self.subscriptions:
            for callback in self.subscriptions[topic]:
                callback(topic, message)
        # Handle wildcard subscriptions
        for wildcard_topic, callback in self.wildcard_subscriptions.items():
            if self.match_wildcard_topic(wildcard_topic, topic):
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
        elif topic in self.wildcard_subscriptions:
            del self.wildcard_subscriptions[topic]

    def reset(self):
        self.subscriptions = {}
        self.wildcard_subscriptions = {}

    def match_wildcard_topic(self, wildcard_topic, topic):
        # Convert wildcard topic to regex
        regex_topic = re.escape(wildcard_topic)
        regex_topic = regex_topic.replace(r'\#', '.*').replace(r'\+', '[^/]+')
        return re.match(f'^{regex_topic}$', topic) is not None

