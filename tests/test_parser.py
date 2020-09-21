from fractions import Fraction

import amalgam.amalgams as am
import amalgam.parser as pr

from pyparsing import ParseException
from pytest import raises


def test_symbol_parser_letters_and_operators():
    letters_and_operators = r"-Spam21?+-*/\&<=>?!_42Eggs!-"
    assert pr.symbol_parser.parseString(letters_and_operators)[0] == am.Symbol(letters_and_operators)


def test_symbol_parser_no_negative_integers():
    with raises(ParseException):
        pr.symbol_parser.parseString(f"-42")


def test_symbol_parser_no_positive_integers():
    with raises(ParseException):
        pr.symbol_parser.parseString(f"+42")


def test_numeric_parser_integral():
    assert pr.numeric_parser.parseString("42")[0] == am.Numeric(42)


def test_numeric_parser_floating():
    assert pr.numeric_parser.parseString("21.42")[0] == am.Numeric(21.42)


def test_numeric_parser_fraction():
    assert pr.numeric_parser.parseString("21/42")[0] == am.Numeric(Fraction(21, 42))


def test_numeric_parser_integral_negative():
    assert pr.numeric_parser.parseString("-42")[0] == am.Numeric(-42)


def test_numeric_parser_floating_negative():
    assert pr.numeric_parser.parseString("-21.42")[0] == am.Numeric(-21.42)


def test_numeric_parser_fraction_negative_numerator():
    assert pr.numeric_parser.parseString("-21/42")[0] == am.Numeric(Fraction(-21, 42))


def test_numeric_parser_fraction_negative_denominator():
    assert pr.numeric_parser.parseString("21/-42")[0] == am.Numeric(Fraction(21, -42))


def test_numeric_parser_fraction_negative_num_denom():
    assert pr.numeric_parser.parseString("-21/-42")[0] == am.Numeric(Fraction(-21, -42))


def test_numeric_parser_floating_raises_ParseException_on_space():
    with raises(ParseException):
        pr.numeric_parser.parseString("21. 42", parseAll=True)

    with raises(ParseException):
        pr.numeric_parser.parseString("21 .42", parseAll=True)


def test_numeric_parser_fraction_raises_ParseException_on_space():
    with raises(ParseException):
        pr.numeric_parser.parseString("21/ 42", parseAll=True)

    with raises(ParseException):
        pr.numeric_parser.parseString("21 /42", parseAll=True)
