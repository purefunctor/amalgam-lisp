from fractions import Fraction
import importlib.resources as resources
import re
from typing import cast

from lark import v_args, Lark, Transformer, UnexpectedInput

import amalgam.amalgams as am


GRAMMAR = resources.read_text(__package__, "grammar.lark")


@v_args(inline=True)
class Expression(Transformer):
    """
    Transforms expressions in text into their respective
    :class:`.amalgams.Amalgam` representations.
    """

    def symbol(self, identifier):
        return am.Symbol(str(identifier)).located_on(
            lines=(identifier.line, identifier.end_line),
            columns=(identifier.column, identifier.end_column),
        )

    def atom(self, colon, identifier):
        return am.Atom(str(identifier)).located_on(
            lines=(colon.line, identifier.end_line),
            columns=(colon.column, identifier.end_column),
        )

    def integral(self, number):
        return am.Numeric(int(number)).located_on(
            lines=(number.line, number.end_line),
            columns=(number.column, number.end_column),
        )

    def floating(self, number):
        return am.Numeric(float(number)).located_on(
            lines=(number.line, number.end_line),
            columns=(number.column, number.end_column),
        )

    def fraction(self, number):
        return am.Numeric(Fraction(number)).located_on(
            lines=(number.line, number.end_line),
            columns=(number.column, number.end_column),
        )

    def string(self, *values):
        l_quote, text, r_quote = values

        value = "".join(values)
        value = re.sub(r"(?<!\\)\\([^\"\\])", r"\g<1>", value)

        return am.String(value.strip("\"")).located_on(
            lines=(l_quote.line, r_quote.line),
            columns=(l_quote.column, r_quote.column),
        )

    def s_expression(self, *values):
        l_paren, *expressions, r_paren = values

        return am.SExpression(*expressions).located_on(
            lines=(l_paren.line, r_paren.end_line),
            columns=(l_paren.column, r_paren.end_column),
        )

    def vector(self, *values):
        l_bracket, *expressions, r_bracket = values

        return am.Vector(*expressions).located_on(
            lines=(l_bracket.line, r_bracket.end_line),
            columns=(l_bracket.column, r_bracket.end_column),
        )

    def quoted(self, quote, expression):
        return am.Quoted(expression).located_on(
            lines=(quote.line, expression.end_line),
            columns=(quote.column, expression.end_column),
        )


class ParsingError(Exception):
    """
    Base exception for errors during parsing.

    Attributes:
      line (:class:`int`): the line number nearest to the error
      column (:class:`int`): the column number nearest to the error
      text (:class:`str`): the original text being parsed
      source (:class:`str`): the source of the original text
    """

    def __init__(self, line: int, column: int, text: str, source: str):
        self.line = line
        self.column = column
        self.text = text
        self.source = source

    def __str__(self):  # pragma: no cover
        return f"in {self.source}, near line {self.line}, column {self.column}"


class ExpectedEOF(ParsingError):
    """Raised when multiple expressions are found."""


class ExpectedExpression(ParsingError):
    """Raised when no expressions are found."""


class MissingClosing(ParsingError):
    """Raised on missing closing parentheses or brackets."""


class MissingOpening(ParsingError):
    """Raised on missing opening parentheses or brackets."""


ERROR_EXAMPLES = {
    ExpectedEOF: ("foo bar",),
    ExpectedExpression: ("",),
    MissingClosing: (
        "(", "[", "(foo", "[foo", "(foo bar", "[foo bar", "\"foo", "\"foo bar",
    ),
    MissingOpening: (
        ")", "]", "[)]", "(])", "[(]", "([)", "[foo bar)", "(foo bar]",
    ),
}


EXPR_PARSER = Lark(GRAMMAR, parser="lalr", transformer=Expression())


def parse(text: str, source: str = "<unknown>") -> am.Amalgam:
    """Facilitates regular parsing that can fail."""
    try:
        return cast(am.Amalgam, EXPR_PARSER.parse(text))
    except UnexpectedInput as u:
        exc_cls = u.match_examples(
            EXPR_PARSER.parse, ERROR_EXAMPLES.items(),
        )
        if exc_cls is None:
            raise
        raise exc_cls(u.line, u.column, text, source) from None
