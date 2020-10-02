from fractions import Fraction

import amalgam.amalgams as am
import amalgam.parser as pr

from pyparsing import ParseException
from pytest import mark, param, raises


def test_symbol_parser_allowed_characters():
    text = r"-+*/<?Spam21&+-*/\&<=>?!_=42Eggs!>\*+-"
    assert pr.symbol_parser.parseString(text)[0] == am.Symbol(text)


def test_symbol_parser_raises_ParseException_on_numerics():
    with raises(ParseException):
        pr.symbol_parser.parseString("1")

    with raises(ParseException):
        pr.symbol_parser.parseString("+1")

    with raises(ParseException):
        pr.symbol_parser.parseString("-1")


def test_string_parser_regular_characters():
    regular = "Spam21 Eggs42 +-*/&<=>?!_="
    assert pr.string_parser.parseString(f"\"{regular}\"")[0] == am.String(regular)


def test_string_parser_escaped_characters():
    regular = "Spam21 Eggs42 +-*/&<=>?!_="
    escaped = "".join(f"\\{character}" for character in regular)
    assert pr.string_parser.parseString(f"\"{escaped}\"")[0] == am.String(regular)


def test_string_parser_escaped_backslash():
    assert pr.string_parser.parseString("\"\\\\\"")[0] == am.String("\\\\")


def test_string_parser_escaped_double_quote():
    regular = "Spam21 Eggs42 +-*/&<=>?!_="
    escaped = f"\\\"{regular}\\\""
    assert pr.string_parser.parseString(f"\"{escaped}\"")[0] == am.String(escaped)


def test_string_parser_raises_ParseException_on_unescaped_quote():
    with raises(ParseException):
        pr.string_parser.parseString("\" \" \"", parseAll=True)


def test_numeric_parser_integral():
    parse_func = pr.numeric_parser.parseString

    unsigned = parse_func("42")[0]
    positive = parse_func("+42")[0]

    assert unsigned == positive == am.Numeric(42)


def test_numeric_parser_floating():
    parse_func = pr.numeric_parser.parseString

    unsigned = parse_func("21.42")[0]
    positive = parse_func("+21.42")[0]

    assert unsigned == positive == am.Numeric(21.42)


def test_numeric_parser_fraction():
    from functools import reduce
    from operator import eq

    parse_func = pr.numeric_parser.parseString

    positives = [
        parse_func(f"{n}/{d}")[0]
        for n in ("21", "+21")
        for d in ("42", "+42")
    ]

    return all(am.Numeric(Fraction(21,42)) == positive for positive in positives)


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


expressions_simple = (
    ("42", am.Numeric(42), "numeric_integral"),
    ("21.42", am.Numeric(21.42), "numeric_floating"),
    ("21/42", am.Numeric(Fraction(21, 42)), "numeric_fraction"),
    ("-+>", am.Symbol("-+>"), "symbol_glyph"),
    ("add", am.Symbol("add"), "symbol_names"),
    ("\"hello, world\"", am.String("hello, world"), "string"),
    ("(+ 42 42)", am.SExpression(am.Symbol("+"), am.Numeric(42), am.Numeric(42)), "s_expression"),
    ("[add 42 42]", am.Vector(am.Symbol("add"), am.Numeric(42), am.Numeric(42)), "vector"),
)


quoted_single = (
    param(f"'{expr_st}", am.Quoted(expr_rs), id=f"{expr_id}-single")
    for expr_st, expr_rs, expr_id in expressions_simple
)

quoted_multi = (
    param(f"''{expr_st}", am.Quoted(am.Quoted(expr_rs)), id=f"{expr_id}-multi")
    for expr_st, expr_rs, expr_id in expressions_simple
)


@mark.parametrize(("expr_s", "expr_r"), (*quoted_single, *quoted_multi))
def test_quoted(expr_s, expr_r):
    assert pr.quoted_parser.parseString(expr_s)[0] == expr_r


def test_s_expression_flat():
    expr_s = "(+ 42 42)"
    expr_r = am.SExpression(am.Symbol("+"), am.Numeric(42), am.Numeric(42))

    assert pr.s_expression_parser.parseString(expr_s)[0] == expr_r


def test_s_expression_nested():
    inner_s = "(+ 42 42)"
    expr_s = f"(+ {inner_s} {inner_s})"

    inner_r = am.SExpression(am.Symbol("+"), am.Numeric(42), am.Numeric(42))
    expr_r = am.SExpression(am.Symbol("+"), inner_r, inner_r)

    assert pr.s_expression_parser.parseString(expr_s)[0] == expr_r


def test_vector_flat():
    vect_s = "[add 42 42]"
    vect_r = am.Vector(am.Symbol("add"), am.Numeric(42), am.Numeric(42))

    assert pr.vector_parser.parseString(vect_s)[0] == vect_r


def test_vector_nested():
    inner_s = "[add 42 42]"
    vect_s = f"[add {inner_s} {inner_s}]"

    inner_r = am.Vector(am.Symbol("add"), am.Numeric(42), am.Numeric(42))
    vect_r = am.Vector(am.Symbol("add"), inner_r, inner_r)

    assert pr.vector_parser.parseString(vect_s)[0] == vect_r
