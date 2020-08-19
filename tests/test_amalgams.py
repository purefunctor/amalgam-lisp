import re
from typing import Any

from amalgam.amalgams import (
    create_fn,
    Amalgam,
    Environment,
    Function,
    Numeric,
    String,
)

from hypothesis import given
from hypothesis.strategies import (
    integers, floats, fractions, text,
    lists, one_of,
)

from pytest import fixture


_non_scientific_float = floats(
    allow_infinity=False,
    allow_nan=False,
).map(str).filter(lambda f: not re.search("[Ee][+-][0-9]+", f)).map(float)

_numeric = one_of(integers(), _non_scientific_float, fractions()).map(Numeric)

_string = text().map(String)


@fixture
def num():
    return Numeric(42)


@fixture
def env():
    return Environment()


def _common_repr(inst: Amalgam):
    return fr"<{inst.__class__.__name__} '[\s\S]+' @ {hex(id(inst))}>"


@given(_numeric)
def test_numeric_evaluate(numeric):
    assert numeric == numeric.evaluate(Environment())


@given(_numeric)
def test_numeric_repr(numeric):
    assert re.match(_common_repr(numeric), repr(numeric))


@given(_string)
def test_string_evaluate(string):
    assert string == string.evaluate(Environment())


@given(_string)
def test_string_repr(string):
    assert re.match(_common_repr(string), repr(string))


def test_function_evaluate_binding(num, env):
    fnc = create_fn("binding-test", "_x", num)
    assert fnc.evaluate(env).env == env


def test_function_evaluate_literal(num, env):
    fnc = create_fn("literal-test", "_x", num)
    assert fnc.evaluate(env).call(num).value == num.value
