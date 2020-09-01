from fractions import Fraction
import re
from typing import Any

from amalgam.amalgams import (
    create_fn,
    Amalgam,
    Deferred,
    Environment,
    Function,
    Numeric,
    String,
    Symbol,
)

from pytest import fixture


def _common_repr(inst: Amalgam):
    return fr"<{inst.__class__.__name__} '[\s\S]+' @ {hex(id(inst))}>"


@fixture
def numerics():
    return Numeric(21), Numeric(21.42), Numeric(Fraction(21, 42))


def test_numeric_evaluate(numerics):
    for numeric in numerics:
        assert numeric == numeric.evaluate(Environment())


def test_numeric_repr(numerics):
    for numeric in numerics:
        assert re.match(_common_repr(numeric), repr(numeric))


@fixture
def strings():
    return String(""), String("\n\t"), String("foo-bar-baz")


def test_string_evaluate(strings):
    for string in strings:
        assert string == string.evaluate(Environment())


def test_string_repr(strings):
    for string in strings:
        assert re.match(_common_repr(string), repr(string))


def test_symbol_evaluate():
    symbol = Symbol("foo")
    environ = Environment(None, {"foo": String("bar")})
    assert symbol.evaluate(environ) == environ["foo"]


def test_symbol_repr():
    symbol = Symbol("foo")
    assert re.match(_common_repr(symbol), repr(symbol))


def test_deferred_evaluate(num, env):
    deferred_one = Deferred(num)
    deferred_many = Deferred(num, num)
    assert deferred_one.evaluate(env) == deferred_one
    assert deferred_many.evaluate(env) == deferred_many


def test_deferred_repr(num, env):
    deferred_one = Deferred(num)
    deferred_many = Deferred(num, num)
    assert re.match(_common_repr(deferred_one), repr(deferred_one))
    assert re.match(_common_repr(deferred_many), repr(deferred_many))


@fixture
def num():
    return Numeric(42)


@fixture
def env():
    return Environment()


def test_function_evaluate_binding(num, env):
    fnc = create_fn("binding-test", "_x", num)
    assert fnc.evaluate(env).env == env


def test_function_evaluate_literal(num, env):
    fnc = create_fn("literal-test", "_x", num)
    assert fnc.evaluate(env).call(num).value == num.value


def test_function_repr(num, env):
    fnc = create_fn("function-test", "_x", num)
    assert re.match(_common_repr(fnc), repr(fnc))


def test_function_evaluate_symbol_global(num, env):
    env["x"] = num
    fnc = create_fn("global-test", "", Symbol("x"))
    assert fnc.evaluate(env).call().value == num.value


def test_function_evaluate_symbol_local(num, env):
    env["x"] = String("fail")
    fnc = create_fn("local-test", "x", Symbol("x"))
    assert fnc.evaluate(env).call(num).value == num.value


def test_function_evaluate_symbol_closure(num, env):
    fnc = create_fn("closure-test", "x", create_fn("inner", "y", Symbol("x")))
    assert fnc.evaluate(env).call(num).call(num).value == num.value
