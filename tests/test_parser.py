import re

from amalgam.parser import numeric_literal, s_expression
from amalgam.parser import IDENTIFIER_PATTERN

from hypothesis import assume, given
from hypothesis.strategies import integers, floats, fractions, from_regex, composite, lists, one_of


_identifier = from_regex(fr"\A{IDENTIFIER_PATTERN}\Z")

_integral = integers().map(str)

_floating = floats(
    allow_infinity=False,
    allow_nan=False,
).map(str).filter(lambda f: not re.search("[Ee][+-][0-9]+", f))

_fraction = fractions().map(str)


@composite
def _arbitrary_s_expressions(draw):
    identifier = draw(_identifier)

    literals = draw(lists(
        one_of(_integral, _floating, _fraction, _identifier)
    ).filter(lambda l: len(l) > 0))

    return f"({identifier} {' '.join(literals)})", ["(", identifier, *literals, ")"]


@given(_identifier)
def test_identifier_pattern(identifier):
    assert not re.match("^-?[0-9]", identifier)


@given(_integral)
def test_numeric_literal_integral(integral):
    assert numeric_literal.parse(integral) == integral


@given(_floating)
def test_numeric_literal_floating(floating):
    assert numeric_literal.parse(floating) == floating


@given(_fraction)
def test_numeric_literal_fraction(fraction):
    assert numeric_literal.parse(fraction) == fraction


@given(_arbitrary_s_expressions())
def test_s_expression_simple(data):
    expression, expected = data
    assert s_expression.parse(expression) == expected


@given(_arbitrary_s_expressions(), _arbitrary_s_expressions())
def test_s_expression_nested(l, r):
    ls, le = l
    rs, re = r

    ts = f"(T {ls} {rs})"
    te = ["(", "T", le, re, ")"]

    assert s_expression.parse(ts) == te


# def test_s_expression_arithmetic_simple():
#     assert s_expression.parse("(+ 21 42)") == ["(", "+", "21", "42", ")"]
#
#
# def test_s_expression_arithmetic_nested():
#     assert s_expression.parse("(+ 21 42 (+ 21 42))") == ["(", "+", "21", "42", ["(", "+", "21", "42", ")"], ")"]
#
#
# def test_s_expression_identifier_simple():
#     assert s_expression.parse("(foo 21 42)") == ["(", "foo", "21", "42", ")"]
#
#
# def test_s_expression_identifier_nested():
#     assert s_expression.parse("(foo 21 42 (bar 21 42))") == ["(", "foo", "21", "42", ["(", "bar", "21", "42", ")"], ")"]
#
#
# def test_s_expression_floating_numbers():
#     assert s_expression.parse("(foo 21.42 42.21)") == ["(", "foo", "21.42", "42.21", ")"]
#
#
# def test_s_expression_rational_numbers():
#     assert s_expression.parse("(foo 21/42 42/21)") == ["(", "foo", "21/42", "42/21", ")"]
