import pytest
from adapters.mqtt_adapter import MQTTAdapter


@pytest.fixture
def mqtt():
    adapter = MQTTAdapter()
    yield adapter
    adapter.reset()


@pytest.fixture
def received_messages():
    return []


def on_message(topic, message, received_messages):
    received_messages.append((topic, message))


def test_exact_topic_subscription(mqtt, received_messages):
    topic = "test/topic"
    message = "test message"

    mqtt.subscribe(topic, lambda t, m: on_message(t, m, received_messages))
    mqtt.publish(topic, message)

    assert (topic, message) in received_messages


def test_single_level_wildcard_subscription(mqtt, received_messages):
    topic = "test/+/subtopic"
    message = "test message"

    mqtt.subscribe(topic, lambda t, m: on_message(t, m, received_messages))
    mqtt.publish("test/one/subtopic", message)
    mqtt.publish("test/two/subtopic", message)

    assert ("test/one/subtopic", message) in received_messages
    assert ("test/two/subtopic", message) in received_messages


def test_multilevel_wildcard_subscription(mqtt, received_messages):
    topic = "test/#"
    message = "test message"

    mqtt.subscribe(topic, lambda t, m: on_message(t, m, received_messages))
    mqtt.publish("test/one/two/three", message)
    mqtt.publish("test/one/two", message)
    mqtt.publish("test/one", message)

    assert ("test/one/two/three", message) in received_messages
    assert ("test/one/two", message) in received_messages
    assert ("test/one", message) in received_messages


def test_mixed_wildcard_subscription(mqtt, received_messages):
    topic = "test/+/subtopic/#"
    message = "test message"

    mqtt.subscribe(topic, lambda t, m: on_message(t, m, received_messages))
    mqtt.publish("test/one/subtopic/level1", message)
    mqtt.publish("test/two/subtopic/level1/level2", message)

    assert ("test/one/subtopic/level1", message) in received_messages
    assert ("test/two/subtopic/level1/level2", message) in received_messages


def test_no_match_subscription(mqtt, received_messages):
    topic = "test/+/subtopic"
    message = "test message"

    mqtt.subscribe(topic, lambda t, m: on_message(t, m, received_messages))
    mqtt.publish("test/one/another", message)
    mqtt.publish("another/test/subtopic", message)

    assert ("test/one/another", message) not in received_messages
    assert ("another/test/subtopic", message) not in received_messages
