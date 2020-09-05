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
    SExpression,
    String,
    Symbol,
    Vector,
)

from pytest import fixture


@fixture
def numerics():
    return Numeric(21), Numeric(21.42), Numeric(Fraction(21, 42))


def test_numeric_evaluate(numerics):
    for numeric in numerics:
        assert numeric == numeric.evaluate(Environment())


@fixture
def strings():
    return String(""), String("\n\t"), String("foo-bar-baz")


def test_string_evaluate(strings):
    for string in strings:
        assert string == string.evaluate(Environment())


def test_symbol_evaluate():
    symbol = Symbol("foo")
    environ = Environment(None, {"foo": String("bar")})
    assert symbol.evaluate(environ) == environ["foo"]


def test_s_expression_evaluate_simple(num, env):
    """
    Simple test for SExpression

    Aside from testing basic usage of SExpression, this test also
    showcases how simple builtin functions are to be implemented.
    """

    # Define the function within Python
    def plus_func(_environment: Environment, x: Numeric, y: Numeric):
        return Numeric(x.value + y.value)

    # Wrap the function inside of a Function
    plus = Function("plus", plus_func)

    # Bind the Function to the environment
    env["plus"] = plus

    # Create the S-Expression
    s_expression = SExpression(Symbol("plus"), num, num)

    # Evaluate the S-Expression
    assert s_expression.evaluate(env).value == num.value + num.value


def test_vector_evaluate_literals(numerics, env):
    vector = Vector(*numerics)
    assert vector.evaluate(env) == vector


def test_vector_evaluate_symbols(numerics, env):
    vector = Vector(*map(Symbol, "xyz"))
    for name, numeric in zip("xyz", numerics):
        env[name] = numeric
    assert vector.evaluate(env) == Vector(*numerics)


def test_deferred_evaluate(num, env):
    deferred = Deferred(num)
    assert deferred.evaluate(env) == deferred


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
