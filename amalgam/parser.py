from fractions import Fraction

import pyparsing as pp

import amalgam.amalgams as am


LPAREN, RPAREN, LBRACE, RBRACE = map(pp.Suppress, "()[]")

symbol_parser = pp.Regex(
    r"(?!-?[0-9])[\+\-\*/\\&<=>?!_a-zA-Z0-9]+"
).setParseAction(
    lambda tokens: am.Symbol(*tokens)
)

string_parser = pp.QuotedString(
    "\"", convertWhitespaceEscapes=False,
).setParseAction(
    lambda tokens: am.String(*tokens)
)

_string_integral_parser = pp.Regex(r"-?(0|[1-9]\d*)")

_integral_parser = _string_integral_parser.copy().setParseAction(
    lambda tokens: int(*tokens)
)

_floating_parser = pp.Combine(
    _string_integral_parser + pp.Literal(".") + pp.Regex(r"\d+")
).setParseAction(
    lambda tokens: float(*tokens)
)

_fraction_parser = (
    _integral_parser + pp.Suppress("/") + _integral_parser
).setParseAction(
    lambda tokens: Fraction(*tokens)
)

numeric_parser = (
    _floating_parser | _fraction_parser | _integral_parser
).setParseAction(
    lambda tokens: am.Numeric(*tokens)
)

_literal_parser = numeric_parser | symbol_parser | string_parser

expression_parser = pp.Forward()

s_expression_parser = (
    LPAREN + expression_parser[...] + RPAREN
).setParseAction(
    lambda tokens: am.SExpression(*tokens)
)

vector_parser = (
    LBRACE + expression_parser[...] + RBRACE
).setParseAction(
    lambda tokens: am.Vector(*tokens)
)

expression_parser <<= _literal_parser | s_expression_parser | vector_parser
