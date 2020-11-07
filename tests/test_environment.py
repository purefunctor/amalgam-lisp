from typing import Any
from itertools import chain

from amalgam.amalgams import Amalgam
from amalgam.environment import (
    Environment,
    TopLevelPop,
)

from pytest import fixture, raises


@fixture
def flat_environment():
    return Environment({"foo": 21, "bar": 42}, engine="engine")


@fixture
def nested_environment():
    return Environment(
        {"foo": 21, "bar": 42}
    ).env_push(
        {"baz": 63, "nil": 84}
    ).env_push(
        {"not": 105, "nul": 126}
    )


def test_environment_copies_bindings():
    bindings = {"x": 21, "y": 42}
    assert Environment(bindings).bindings is not bindings


def test_environment_increments_level(flat_environment):
    assert flat_environment.level == 0
    assert Environment(parent=flat_environment).level == 1


def test_environment_env_push(flat_environment):
    bindings = {"x": 21, "y": 42}
    new_env = flat_environment.env_push(bindings, "env")

    assert new_env.parent == flat_environment
    assert new_env.bindings == bindings
    assert new_env.level == flat_environment.level + 1
    assert new_env.name == "env"
    assert new_env.engine == flat_environment.engine
    assert new_env.env_push().name == "env-child"


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

    with raises(KeyError):
        flat_environment["nil"]


def test_environment_setitem_immediate(flat_environment):
    flat_environment["foo"] = 84
    flat_environment["new"] = 42

    assert flat_environment.bindings["foo"] == 84
    assert flat_environment.bindings["new"] == 42


def test_environment_delitem_immediate(flat_environment):
    del flat_environment["foo"]

    assert "foo" not in flat_environment.bindings

    with raises(KeyError):
        del flat_environment["nil"]


def test_environment_contains_immediate(flat_environment):
    assert "foo" in flat_environment
    assert "new" not in flat_environment


def test_environment_getitem_infinite(nested_environment):
    with nested_environment.search_at(depth=-1):
        assert nested_environment["nul"] == nested_environment.bindings["nul"]
        assert nested_environment["baz"] == nested_environment.parent.bindings["baz"]
        assert nested_environment["foo"] == nested_environment.parent.parent.bindings["foo"]

    with raises(KeyError):
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
        with raises(KeyError):
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
        with raises(KeyError):
            del nested_environment["foo"]


def test_environment_contains_limited(nested_environment):
    with nested_environment.search_at(depth=1):
        assert "nul" in nested_environment
        assert "baz" in nested_environment
        assert "foo" not in nested_environment
