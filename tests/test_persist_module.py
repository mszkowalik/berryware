import pytest
import os
from adapters.persist_adapter import PersistAdapter


@pytest.fixture
def persist():
    filename = "./_persist_test.json"
    persist = PersistAdapter(filename)
    persist.zero()
    persist.save()
    yield persist
    # Teardown code: remove the test file after each test
    if os.path.exists(filename):
        os.remove(filename)


def test_set_and_get_attribute(persist):
    persist.a = 1
    assert persist.a == 1


def test_save_and_load(persist):
    persist.a = 1
    persist.save()

    new_persist = PersistAdapter(persist.filename)
    assert new_persist.a == 1


def test_has_key(persist):
    persist.a = 1
    assert persist.has("a") is True
    assert persist.has("b") is False


def test_remove_key(persist):
    persist.a = 1
    assert persist.remove("a") is True
    assert persist.has("a") is False
    assert persist.remove("b") is False


def test_find_key(persist):
    persist.a = 1
    assert persist.find("a") == 1
    assert persist.find("b") is None
    assert persist.find("b", "default") == "default"


def test_member_key(persist):
    persist.a = 1
    assert persist.member("a") == 1
    assert persist.member("b") is None


def test_setmember(persist):
    persist.setmember("a", 1)
    assert persist.a == 1


def test_zero(persist):
    persist.a = 1
    persist.b = 2
    persist.zero()
    assert persist.a is None
    assert persist.b is None
