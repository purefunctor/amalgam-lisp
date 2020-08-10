from collections import namedtuple
from functools import partial
import re

from amalgam.parser import numeric_literal, s_expression
from amalgam.parser import IDENTIFIER_PATTERN

from hypothesis import assume, given
from hypothesis.strategies import integers, floats, fractions, from_regex, lists, one_of, composite, recursive, builds


_identifier = from_regex(fr"\A{IDENTIFIER_PATTERN}\Z")

_integral = integers().map(str)

_floating = floats(
    allow_infinity=False,
    allow_nan=False,
).map(str).filter(lambda f: not re.search("[Ee][+-][0-9]+", f))

_fraction = fractions().map(str)

_literals = lists(
    one_of(_integral, _floating, _fraction)
).filter(lambda l: len(l) > 0)


@composite
def _recursive_literals(draw):
    pair = namedtuple("pair", "iden succ")
    coll = namedtuple("coll", "vals")

    chosen = draw(recursive(_literals.map(coll), partial(builds, pair, _identifier)))

    def as_string(chosen):
        if isinstance(chosen, coll):
            return " ".join(chosen.vals)
        elif isinstance(chosen, pair):
            return f"({chosen.iden} {as_string(chosen.succ)})"

    def as_structure(chosen, *, recurse=False):
        if isinstance(chosen, coll):
            return chosen if recurse else chosen.vals
        elif isinstance(chosen, pair):
            succ = as_structure(chosen.succ, recurse=True)
            if isinstance(succ, coll):
                return ["(", chosen.iden, *succ.vals, ")"]
            return ["(", chosen.iden, succ, ")"]

    return as_string(chosen), as_structure(chosen)


@given(_identifier)
def test_identifier_pattern(identifier):
    assert not re.match("[0-9]", identifier[0])


@given(_integral)
def test_numeric_literal_integral(integral):
    assert numeric_literal.parse(integral) == integral


@given(_floating)
def test_numeric_literal_floating(floating):
    assert numeric_literal.parse(floating) == floating


@given(_fraction)
def test_numeric_literal_fraction(fraction):
    assert numeric_literal.parse(fraction) == fraction


@given(_identifier, _literals)
def test_s_expression_literals(identifier, literals):
    assert s_expression.parse(f"({identifier} {' '.join(literals)})") == ["(", identifier, *literals, ")"]


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
