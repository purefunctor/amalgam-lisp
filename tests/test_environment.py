from typing import Any
from itertools import chain

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


@fixture
def nested():
    e0 = Environment(None, {v: DummyAmalgam(v) for v in ("foo", "bar" "baz")})
    e1 = Environment(e0, {v: DummyAmalgam(v) for v in ("ifoo", "ibar", "ibaz")})
    return e1


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


def test_immediate_environment_push(immediate):
    assert immediate.env_push().parent == immediate


def test_immediate_environment_pop_fails(immediate):
    with raises(Exception):
        immediate.env_pop()


def test_nested_environment_iget(nested):
    assert nested.iget("ifoo") == nested.bindings.get("ifoo")


def test_nested_environment_iget_fails(nested):
    with raises(KeyError):
        nested.iget("key-error")


def test_nested_environment_iset(nested):
    nested.iset("ifoo", 42)
    assert nested.bindings.get("ifoo") == 42


def test_nested_environment_idel(nested):
    nested.idel("ifoo")
    assert nested.bindings.get("ifoo", None) == None


def test_nested_environment_idel_fails(nested):
    with raises(KeyError):
        nested.idel("key-error")


def test_nested_environment_ihas(nested):
    assert nested.ihas("ifoo") == ("ifoo" in nested.bindings)
    assert nested.ihas("null") == ("null" in nested.bindings)


def test_nested_environment_iiter(nested):
    assert list(nested.iiter()) == list(iter(nested.bindings))


def test_nested_environment_ilen(nested):
    assert nested.ilen() == len(nested.bindings)


def test_nested_environment_getitem(nested):
    assert nested["ifoo"] == nested.bindings.get("ifoo")
    assert nested["foo"] == nested.parent.bindings.get("foo")


def test_nested_environment_getitem_fails(nested):
    with raises(KeyError):
        nested["key-error"]


def test_nested_environment_setitem(nested):
    nested["ifoo"] = 21
    nested["foo"] = 42
    assert nested.bindings.get("ifoo") == 21
    assert nested.parent.bindings.get("foo") == 42


def test_nested_environment_delitem(nested):
    del nested["ifoo"]
    del nested["foo"]
    assert nested.bindings.get("ifoo", None) == None
    assert nested.parent.bindings.get("foo", None) == None


def test_nested_environment_delitem_fails(nested):
    with raises(KeyError):
        del nested["key-error"]


def test_nested_environment_contains(nested):
    assert ("ifoo" in nested) == ("ifoo" in nested.bindings)
    assert ("foo" in nested) == ("foo" in nested.parent.bindings)
    assert ("null" in nested) == ("null" in nested.bindings) == ("null" in nested.parent.bindings)


def test_nested_environment_iter(nested):
    assert list(iter(nested)) == list(chain(iter(nested.parent.bindings), nested.bindings))


def test_nested_environment_len(nested):
    assert len(nested) == len(nested.parent.bindings) + len(nested.bindings)


def test_nested_environment_push(nested):
    assert nested.env_push().parent == nested


def test_nested_environment_pop(nested):
    assert nested.env_pop() == nested.parent
