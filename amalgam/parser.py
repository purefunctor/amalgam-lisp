from fractions import Fraction
import importlib.resources as resources
from io import StringIO
import re
from typing import cast, Optional

from lark import v_args, Lark, Token, Transformer, UnexpectedInput

import amalgam.amalgams as am


GRAMMAR = resources.read_text(__package__, "grammar.lark")


@v_args(inline=True)
class Expression(Transformer):
    """
    Transforms expressions in text into their respective
    :class:`.amalgams.Amalgam` representations.
    """

    def symbol(self, identifier: Token) -> am.Symbol:
        return am.Symbol(str(identifier))

    def atom(self, identifier: Token) -> am.Atom:
        return am.Atom(str(identifier))

    def integral(self, number: Token) -> am.Numeric:
        return am.Numeric(int(number))

    def floating(self, number: Token) -> am.Numeric:
        return am.Numeric(float(number))

    def fraction(self, number: Token) -> am.Numeric:
        return am.Numeric(Fraction(number))

    def string(self, *values: Token) -> am.String:
        value = "".join(values)
        value = re.sub(r"(?<!\\)\\([^\"\\])", r"\g<1>", value)
        return am.String(value.strip("\""))

    def s_expression(self, *expressions: am.Amalgam) -> am.SExpression:
        return am.SExpression(*expressions)

    def vector(self, *expressions: am.Amalgam) -> am.Vector:
        return am.Vector(*expressions)

    def quoted(self, expression: am.Amalgam) -> am.Quoted:
        return am.Quoted(expression)


class ParsingError(Exception):
    """
    Base exception for errors during parsing.

    Attributes:
      line (:class:`int`): the line number nearest to the error
      column (:class:`int`): the column number nearest to the error
    """

    def __init__(self, line: int, column: int):
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

    Attributes:
      parse_buffer (:class:`StringIO`): The text buffer used within
        :meth:`.Parser.repl_parse`.
    """

    def __init__(self) -> None:
        self.parse_buffer = StringIO()

    def repl_parse(self, text: str) -> Optional[am.Amalgam]:
        """
        Facilitates multi-line parsing for the REPL.

        Writes the given `text` string to the :attr:`parse_buffer` and
        attempts to parse `text`.

        If :class:`MissingClosing` is raised, returns `None` to allow
        for parsing to continue.

        If another subclass of :class:`ParsingError` is raised, clears
        the :attr:`parse_buffer` and re-raises the exception.

        Otherwise, if parsing succeeds, clears the :attr:`parse_buffer`
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
