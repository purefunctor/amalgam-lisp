import re

from amalgam.parser import numeric_literal, s_expression
from amalgam.parser import IDENTIFIER_PATTERN

from hypothesis import assume, given
from hypothesis.strategies import integers, floats, fractions, from_regex


_random_identifier = from_regex(fr"\A{IDENTIFIER_PATTERN}\Z")


@given(_random_identifier)
def test_identifier_pattern(identifier):
    assert not re.match("[0-9]", identifier[0])


@given(integers().map(str))
def test_numeric_literal_integral(integral):
    assert numeric_literal.parse(integral) == integral


@given(floats(allow_infinity=False, allow_nan=False).map(str))
def test_numeric_literal_floating(floating):
    assume(not re.search("[Ee][+-][0-9]+", floating))
    assert numeric_literal.parse(floating) == floating


@given(fractions().map(str))
def test_numeric_literal_fraction(fraction):
    assert numeric_literal.parse(fraction) == fraction


def test_s_expression_arithmetic_simple():
    assert s_expression.parse("(+ 21 42)") == ["(", "+", "21", "42", ")"]


def test_s_expression_arithmetic_nested():
    assert s_expression.parse("(+ 21 42 (+ 21 42))") == ["(", "+", "21", "42", ["(", "+", "21", "42", ")"], ")"]


def test_s_expression_identifier_simple():
    assert s_expression.parse("(foo 21 42)") == ["(", "foo", "21", "42", ")"]


def test_s_expression_identifier_nested():
    assert s_expression.parse("(foo 21 42 (bar 21 42))") == ["(", "foo", "21", "42", ["(", "bar", "21", "42", ")"], ")"]


def test_s_expression_floating_numbers():
    assert s_expression.parse("(foo 21.42 42.21)") == ["(", "foo", "21.42", "42.21", ")"]


def test_s_expression_rational_numbers():
    assert s_expression.parse("(foo 21/42 42/21)") == ["(", "foo", "21/42", "42/21", ")"]
