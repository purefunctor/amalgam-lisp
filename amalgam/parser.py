from fractions import Fraction
import importlib.resources as resources
from io import StringIO
import re
from typing import cast, Optional

from lark import v_args, Lark, Transformer, UnexpectedInput

import amalgam.amalgams as am


GRAMMAR = resources.read_text(__package__, "grammar.lark")


@v_args(inline=True)
class Expression(Transformer):
    def symbol(self, identifier):
        return am.Symbol(identifier)

    def atom(self, identifier):
        return am.Atom(identifier)

    def integral(self, number):
        return am.Numeric(int(number))

    def floating(self, number):
        return am.Numeric(float(number))

    def fraction(self, number):
        return am.Numeric(Fraction(number))

    def string(self, *values):
        value = "".join(values)
        value = re.sub(r"(?<!\\)\\([^\"\\])", r"\g<1>", value)
        return am.String(value.strip("\""))

    def s_expression(self, *expressions):
        return am.SExpression(*expressions)

    def vector(self, *expressions):
        return am.Vector(*expressions)

    def quoted(self, expression):
        return am.Quoted(expression)


class ParsingError(Exception):
    """Base exception for errors during parsing."""

    def __init__(self, line, column):
        self.line = line
        self.column = column

    def __str__(self):  # pragma: no cover
        return f"near line {self.line}, column {self.column}"


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
    MissingOpening: (")", "]", "[foo bar)", "(foo bar]"),
}


EXPR_PARSER = Lark(GRAMMAR, parser="lalr", transformer=Expression())


class Parser:
    """
    Class that serves as the frontend for parsing text.
    """

    def __init__(self) -> None:
        self.parse_buffer = StringIO()

    def repl_parse(self, text: str) -> Optional[am.Amalgam]:
        """
        Facilitates multi-line parsing for the REPL.

        Writes the given `text` string to the `parse_buffer` attribute
        and attempts to parse `text`.

        If `MissingClosing` is raised, returns `None` to allow for
        parsing to continue.

        If another subclass of `ParsingError` is raised, clears the
        `parse_buffer` and re-raises the exception.

        Otherwise, if parsing succeeds, clears the `parse_buffer`
        and returns the parsed expression.
        """
        self.parse_buffer.write(text)
        self.parse_buffer.seek(0)
        text = self.parse_buffer.read()

        try:
            expr = self.parse(text)

        except MissingClosing:
            return None

        except (UnexpectedInput, ParsingError):
            self.parse_buffer = StringIO()
            raise

        else:
            self.parse_buffer = StringIO()
            return expr

    def parse(self, text: str) -> am.Amalgam:
        """Facilitates regular parsing that can fail."""
        try:
            return cast(am.Amalgam, EXPR_PARSER.parse(text))
        except UnexpectedInput as u:
            exc_cls = u.match_examples(
                EXPR_PARSER.parse, ERROR_EXAMPLES.items(),
            )
            if exc_cls is None:
                raise
            raise exc_cls(u.line, u.column) from None
