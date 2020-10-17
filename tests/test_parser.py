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


def test_atom_parser_allowed_characters():
    text = r":-+*/<?Spam21&+-*/\&<=>?!_=42Eggs!>\*+-"
    assert pr.atom_parser.parseString(text)[0] == am.Atom(text[1:])


def test_atom_raises_ParseException():
    with raises(ParseException):
        pr.atom_parser.parseString(":123")

    with raises(ParseException):
        pr.atom_parser.parseString("+123")

    with raises(ParseException):
        pr.atom_parser.parseString("-123")

    with raises(ParseException):
        pr.atom_parser.parseString("xyz")

    with raises(ParseException):
        pr.atom_parser.parseString("=+-")


_string_contents = "Spam21 Eggs42 +-*/&<=>?!_="
_escaped_characters = "".join(map("\\{}".format, _string_contents))

strings = (
    param(expr_st, expr_rs, id=expr_id)
    for expr_st, expr_rs, expr_id in (
        (f"\"{_string_contents}\"", am.String(_string_contents), "regular-string"),
        (f"\"{_escaped_characters}\"", am.String(_string_contents), "escaped-characters"),
        ("\"\\\\\"", am.String("\\\\"), "escaped-backslash"),
        ("\"\\\"\\\"\"", am.String("\\\"\\\""), "escaped-quotes"),
    )
)


@mark.parametrize(("expr_s", "expr_r"), strings)
def test_string_parser(expr_s, expr_r):
    assert pr.string_parser.parseString(expr_s)[0] == expr_r


def test_string_parser_raises_ParseException_on_unescaped_quote():
    with raises(ParseException):
        pr.string_parser.parseString("\" \" \"", parseAll=True)


numerics = (
    param(expr_st, expr_rs, id=expr_id)
    for expr_st, expr_rs, expr_id in (
        ("42", am.Numeric(42), "unsigned-integral"),
        ("+42", am.Numeric(42), "positive-integral"),
        ("-42", am.Numeric(-42), "negative-integral"),
        ("21.42", am.Numeric(21.42), "unsigned-floating"),
        ("+21.42", am.Numeric(21.42), "positive-floating"),
        ("-21.42", am.Numeric(-21.42), "negative-floating"),
        ("21/42", am.Numeric(Fraction(21, 42)), "unsigned-fraction"),
        ("+21/42", am.Numeric(Fraction(21, 42)), "positive-fraction-numerator"),
        ("-21/42", am.Numeric(Fraction(-21, 42)), "negative-fraction-numerator"),
        ("21/+42", am.Numeric(Fraction(21, 42)), "positive-fraction-denominator"),
        ("21/-42", am.Numeric(Fraction(21, -42)), "negative-fraction-denominator"),
        ("+21/+42", am.Numeric(Fraction(21, 42)), "positive-fraction"),
        ("-21/-42", am.Numeric(Fraction(-21, -42)), "negative-fraction"),
    )
)


@mark.parametrize(("expr_s", "expr_r"), numerics)
def test_numeric_parser(expr_s, expr_r):
    assert pr.numeric_parser.parseString(expr_s)[0] == expr_r


numerics_invalid = (
    param(expr_st, id=expr_id)
    for expr_st, expr_id in (
        ("21. 42", "floating-space-after-period"),
        ("21 .42", "floating-space-before-period"),
        ("21 . 42", "floating-space-after-and-before-period"),
        ("21/ 42", "fraction-space-after-slash"),
        ("21 /42", "fraction-space-before-slash"),
        ("21 / 42", "fraction-space-after-and-before-slash"),
    )
)


@mark.parametrize("expr_s", numerics_invalid)
def test_numeric_parser_raises_ParseException_on(expr_s):
    with raises(ParseException):
        pr.numeric_parser.parseString(expr_s, parseAll=True)


expressions_simple = (
    ("42", am.Numeric(42), "numeric_integral"),
    ("21.42", am.Numeric(21.42), "numeric_floating"),
    ("21/42", am.Numeric(Fraction(21, 42)), "numeric_fraction"),
    ("-+>", am.Symbol("-+>"), "symbol_glyph"),
    ("add", am.Symbol("add"), "symbol_names"),
    (":-+>", am.Atom("-+>"), "atom_glyphs"),
    (":TRUE", am.Atom("TRUE"), "atom_names"),
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


_s_expression_flat = am.SExpression(am.Symbol("+"), am.Numeric(42), am.Numeric(42))
_s_expression_nested = am.SExpression(am.Symbol("+"), _s_expression_flat, _s_expression_flat)
s_expressions = (
    param(expr_st, expr_rs, id=expr_id)
    for expr_st, expr_rs, expr_id in (
        ("(+ 42 42)", _s_expression_flat, "flat"),
        ("(+ (+ 42 42) (+ 42 42))", _s_expression_nested, "nested"),
    )
)


@mark.parametrize(("expr_s", "expr_r"), s_expressions)
def test_s_expression(expr_s, expr_r):
    assert pr.s_expression_parser.parseString(expr_s)[0] == expr_r


_vector_flat = am.Vector(am.Symbol("add"), am.Numeric(42), am.Numeric(42))
_vector_nested = am.Vector(am.Symbol("add"), _vector_flat, _vector_flat)
vectors = [
    param(expr_st, expr_rs, id=expr_id)
    for expr_st, expr_rs, expr_id in (
        ("[add 42 42]", _vector_flat, "flat"),
        ("[add [add 42 42] [add 42 42]]", _vector_nested, "nested")
    )
]


@mark.parametrize(("expr_s", "expr_r"), vectors)
def test_vector(expr_s, expr_r):
    assert pr.vector_parser.parseString(expr_s)[0] == expr_r


def test_AmalgamParser_raises_ParseException():
    repl_parser = pr.AmalgamParser()

    with raises(ParseException):
        repl_parser.parse("1 . 0")


def test_AmalgamParser_bracket_mismatch():
    repl_parser = pr.AmalgamParser()

    with raises(ParseException):
        repl_parser.parse("(+ 1 2]")

    with raises(ParseException):
        repl_parser.parse("[1 2 3)")


continuations = (
    param(cont_first, cont_then, id=cont_iden)
    for cont_first, cont_then, cont_iden in (
        ("(+ 1", "\n1)", "s-expression"),
        ("[1 2", "\n3]", "vector"),
        ("\"fo", "\no\"", "string"),
        ("(+ 1 [1 2", "\n3 4])", "s-expression-vector"),
        ("[1 2 (+ 1", "\n3 4)]", "vector-s-expression"),
        ("(+ 1 \"fo", "\no\")", "s-expression-string"),
        ("[+ 1 \"fo", "\no\"]", "vector-string"),

    )
)


@mark.parametrize(("cont_first", "cont_then"), continuations)
def test_AmalgamParser_multiline_continuation(cont_first, cont_then):
    repl_parser = pr.AmalgamParser()

    cont_full = cont_first + cont_then

    assert repl_parser.parse(cont_first) == None
    assert repl_parser.expect_more == True
    assert repl_parser.parse_buffer.tell() == len(cont_first)

    assert repl_parser.parse(cont_then) == pr.expression_parser.parseString(cont_full)[0]
    assert repl_parser.expect_more == False
    assert repl_parser.parse_buffer.tell() == 0
