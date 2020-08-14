from typing import Any

from amalgam.amalgams import Amalgam, Environment

from pytest import fixture, raises


class DummyAmalgam(Amalgam):
    """A dummy subclass of `Amalgam` used for testing."""

    def __init__(self, value: str):
        self.value: str = value

    def evaluate(self, environment: Environment, *arguments: Any) -> Any:
        return None


@fixture
def immediate():
    return Environment(None, {v: DummyAmalgam(v) for v in ("foo", "bar", "baz")})


def test_immediate_environment_iget(immediate):
    assert immediate.iget("foo") == immediate.bindings.get("foo")


def test_immediate_environment_iget_fails(immediate):
    with raises(KeyError):
        immediate.iget("key-error")


def test_immediate_environment_iset(immediate):
    immediate.iset("foo", 42)
    assert immediate.bindings.get("foo") == 42


def test_immediate_environment_idel(immediate):
    immediate.idel("foo")
    assert immediate.bindings.get("foo", None) == None


def test_immediate_environment_idel_fails(immediate):
    with raises(KeyError):
        immediate.idel("key-error")


def test_immediate_environment_ihas(immediate):
    assert immediate.ihas("foo") == ("foo" in immediate.bindings)
    assert immediate.ihas("nul") == ("nul" in immediate.bindings)


def test_immediate_environment_iiter(immediate):
    assert list(immediate.iiter()) == list(iter(immediate.bindings))


def test_immediate_environment_ilen(immediate):
    assert immediate.ilen() == len(immediate.bindings)


def test_immediate_environment_getitem(immediate):
    assert immediate["foo"] == immediate.iget("foo")


def test_immediate_environment_getitem_fails(immediate):
    with raises(KeyError):
        immediate["key-error"]


def test_immediate_environment_settitem(immediate):
    immediate["foo"] = 42
    assert immediate.bindings.get("foo") == 42


def test_immediate_environment_delitem(immediate):
    del immediate["foo"]
    assert immediate.bindings.get("foo", None) == None


def test_immediate_environment_delitem_fails(immediate):
    with raises(KeyError):
        del immediate["key-error"]


def test_immediate_environment_contains(immediate):
    assert ("foo" in immediate) == ("foo" in immediate.bindings)


def test_immediate_environment_iter(immediate):
    assert list(iter(immediate)) == list(iter(immediate.bindings))


def test_immediate_environment_len(immediate):
    assert len(immediate) == len(immediate.bindings)
