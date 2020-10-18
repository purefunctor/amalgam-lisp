from typing import Any
from itertools import chain

from amalgam.amalgams import (
    Amalgam,
    Environment,
    _Environment,
    SymbolNotFound,
    TopLevelPop,
)

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
    assert list(immediate.iiter()) == list(immediate.bindings)


def test_immediate_environment_ilen(immediate):
    assert immediate.ilen() == len(immediate.bindings)


def test_immediate_environment_getitem(immediate):
    assert immediate["foo"] == immediate.bindings.get("foo")


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
    assert ("nil" in immediate) == ("nil" in immediate.bindings)


def test_immediate_environment_iter(immediate):
    assert list(immediate) == list(immediate.bindings)


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
    assert list(nested.iiter()) == list(nested.bindings)


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
    assert list(nested) == list(chain(nested.parent.bindings, nested.bindings))


def test_nested_environment_len(nested):
    assert len(nested) == len(nested.parent.bindings) + len(nested.bindings)


def test_nested_environment_push(nested):
    assert nested.env_push().parent == nested


def test_nested_environment_pop(nested):
    assert nested.env_pop() == nested.parent


@fixture
def flat_environment():
    return _Environment({"foo": 21, "bar": 42})


@fixture
def nested_environment():
    return _Environment(
        {"foo": 21, "bar": 42}
    ).env_push(
        {"baz": 63, "nil": 84}
    ).env_push(
        {"not": 105, "nul": 126}
    )


def test_environment_copies_bindings():
    bindings = {"x": 21, "y": 42}
    assert _Environment(bindings).bindings is not bindings


def test_environment_increments_level(flat_environment):
    assert flat_environment.level == 0
    assert _Environment(parent=flat_environment).level == 1


def test_environment_env_push(flat_environment):
    bindings = {"x": 21, "y": 42}
    new_env = flat_environment.env_push(bindings)

    assert new_env.parent == flat_environment
    assert new_env.bindings == bindings
    assert new_env.level == flat_environment.level + 1


def test_environment_env_pop(flat_environment):
    assert flat_environment.env_push().env_pop() is flat_environment

    with raises(TopLevelPop):
        flat_environment.env_pop()


def test_environment_search_at(nested_environment):
    with nested_environment.search_at(depth=1):
        assert nested_environment.search_depth == 1
    assert nested_environment.search_depth == 0

    with nested_environment.search_at(depth=-1):
        assert nested_environment.search_depth == -1
    assert nested_environment.search_depth == 0

    with raises(ValueError):
        with nested_environment.search_at(depth=3):
            pass


def test_environment_getitem_immediate(flat_environment):
    assert flat_environment["foo"] == flat_environment.bindings["foo"]

    with raises(SymbolNotFound):
        flat_environment["nil"]


def test_environment_setitem_immediate(flat_environment):
    flat_environment["foo"] = 84
    flat_environment["new"] = 42

    assert flat_environment.bindings["foo"] == 84
    assert flat_environment.bindings["new"] == 42


def test_environment_delitem_immediate(flat_environment):
    del flat_environment["foo"]

    assert "foo" not in flat_environment.bindings

    with raises(SymbolNotFound):
        del flat_environment["nil"]


def test_environment_contains_immediate(flat_environment):
    assert "foo" in flat_environment
    assert "new" not in flat_environment


def test_environment_getitem_infinite(nested_environment):
    with nested_environment.search_at(depth=-1):
        assert nested_environment["nul"] == nested_environment.bindings["nul"]
        assert nested_environment["baz"] == nested_environment.parent.bindings["baz"]
        assert nested_environment["foo"] == nested_environment.parent.parent.bindings["foo"]

    with raises(SymbolNotFound):
        with nested_environment.search_at(depth=-1):
            nested_environment["new"]


def test_environment_setitem_infinite(nested_environment):
    with nested_environment.search_at(depth=-1):
        nested_environment["nul"] = 21
        nested_environment["baz"] = 42
        nested_environment["foo"] = 63

    assert nested_environment.bindings["nul"] == 21
    assert nested_environment.parent.bindings["baz"] == 42
    assert nested_environment.parent.parent.bindings["foo"] == 63


def test_environment_delitem_infinite(nested_environment):
    with nested_environment.search_at(depth=-1):
        del nested_environment["nul"]
        del nested_environment["baz"]
        del nested_environment["foo"]

    assert "nul" not in nested_environment.bindings
    assert "baz" not in nested_environment.parent.bindings
    assert "foo" not in nested_environment.parent.parent.bindings


def test_environment_contains_infinite(nested_environment):
    with nested_environment.search_at(depth=-1):
        assert "nul" in nested_environment
        assert "baz" in nested_environment
        assert "foo" in nested_environment
        assert "new" not in nested_environment


def test_environment_getitem_limited(nested_environment):
    with nested_environment.search_at(depth=1):
        assert nested_environment["nul"] == nested_environment.bindings["nul"]
        assert nested_environment["baz"] == nested_environment.parent.bindings["baz"]

    with nested_environment.search_at(depth=1):
        with raises(SymbolNotFound):
            nested_environment["foo"]


def test_environment_setitem_limited(nested_environment):
    with nested_environment.search_at(depth=1):
        nested_environment["nul"] = 21
        nested_environment["baz"] = 42
        nested_environment["foo"] = 63

    assert nested_environment.bindings["nul"] == 21
    assert nested_environment.parent.bindings["baz"] == 42
    assert nested_environment.parent.bindings["foo"] == 63


def test_environment_delitem_limited(nested_environment):
    with nested_environment.search_at(depth=1):
        del nested_environment["nul"]
        del nested_environment["baz"]

    assert "nul" not in nested_environment.bindings
    assert "baz" not in nested_environment.parent.bindings

    with nested_environment.search_at(depth=1):
        with raises(SymbolNotFound):
            del nested_environment["foo"]


def test_environment_contains_limited(nested_environment):
    with nested_environment.search_at(depth=1):
        assert "nul" in nested_environment
        assert "baz" in nested_environment
        assert "foo" not in nested_environment
