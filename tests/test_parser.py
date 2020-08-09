import re

from amalgam.parser import s_expression
from amalgam.parser import IDENTIFIER_PATTERN, NUMERIC_PATTERN

from hypothesis import assume, given
from hypothesis.strategies import integers, floats, fractions, from_regex


_random_identifier = from_regex(fr"\A{IDENTIFIER_PATTERN}\Z")


@given(_random_identifier)
def test_identifier_pattern(identifier):
    assert not re.match("[0-9]", identifier[0])


@given(integers())
def test_numeric_integer_pattern(integer):
    assert re.match(NUMERIC_PATTERN, str(integer))


@given(floats(allow_infinity=False, allow_nan=False))
def test_numeric_floating_pattern(floating):
    assume(not re.search("[Ee][+-][0-9]+", str(floating)))
    assert re.match(NUMERIC_PATTERN, str(floating))


@given(fractions())
def test_numeric_fraction_pattern(fraction):
    assert re.match(NUMERIC_PATTERN, str(fraction))


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
