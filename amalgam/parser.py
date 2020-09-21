from fractions import Fraction
from functools import wraps

import pyparsing as pp

import amalgam.amalgams as am


def apply_splat(func):
    """
    Helper function for splatting args to callbacks.

    Takes a callable `func` and return a function of one
    argument `tokens` and splats `tokens` into `func`.
    """

    @wraps(func)
    def _(tokens):
        return func(*tokens)

    return _


LPAREN, RPAREN, LBRACE, RBRACE = map(pp.Suppress, "()[]")

symbol_parser = pp.Regex(
    r"(?!-?[0-9])[\+\-\*/\\&<=>?!_a-zA-Z0-9]+"
).setParseAction(
    apply_splat(am.Symbol)
)

string_parser = pp.QuotedString(
    "\"", convertWhitespaceEscapes=False,
).setParseAction(
    apply_splat(am.String)
)

_string_integral_parser = pp.Regex(r"-?(0|[1-9]\d*)")

_integral_parser = _string_integral_parser.copy().setParseAction(
    apply_splat(int)
)

_floating_parser = pp.Combine(
    _string_integral_parser + pp.Literal(".") + pp.Regex(r"\d+")
).setParseAction(
    apply_splat(float)
)

_fraction_parser = (
    _integral_parser
    + pp.Suppress("/").leaveWhitespace()
    + _integral_parser.copy().leaveWhitespace()
).setParseAction(
    apply_splat(Fraction)
)

numeric_parser = (
    _floating_parser | _fraction_parser | _integral_parser
).setParseAction(
    apply_splat(am.Numeric)
)

expression_parser = pp.Forward()

quoted_parser = (
    pp.Suppress("'") + expression_parser
).setParseAction(
    apply_splat(am.Quoted)
)

s_expression_parser = (
    LPAREN + expression_parser[...] + RPAREN
).setParseAction(
    apply_splat(am.SExpression)
)

vector_parser = (
    LBRACE + expression_parser[...] + RBRACE
).setParseAction(
    apply_splat(am.Vector)
)

expression_parser <<= (
    quoted_parser
    | numeric_parser
    | symbol_parser
    | string_parser
    | s_expression_parser
    | vector_parser
)
