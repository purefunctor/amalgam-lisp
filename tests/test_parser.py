import amalgam.parser as pr

from pytest import fixture, mark, param, raises


def test_symbol_parser_allowed_characters():
    text = r"-+*/<?Spam21&+-*/\&<=>?!_=42Eggs!>\*+-"
    assert text == str(pr.parse(text))


def test_atom_parser_allowed_characters():
    text = r":-+*/<?Spam21&+-*/\&<=>?!_=42Eggs!>\*+-"
    assert text == str(pr.parse(text))


_string_contents = "Spam21 Eggs42 +-*/&<=>?!_="
_escaped_characters = "".join(map("\\{}".format, _string_contents))
_as_string = "\"{}\"".format


strings = (
    param(string, id=expr_id)
    for string, expr_id in (
        (_as_string(_string_contents), "regular-string"),
        (_as_string(_escaped_characters), "escaped-characters"),
        (_as_string("\\\\"), "escaped-backslash"),
        (_as_string("\\\""), "escaped-quotes"),
    )
)


@mark.parametrize(("string",), strings)
def test_string_parser(string):
    parsed = pr.parse(string)
    assert _as_string(parsed.value) == str(parsed)


numerics = (
    param(numeric, id=expr_id)
    for numeric, expr_id in (
        ("42", "unsigned-integral"),
        ("-42", "negative-integral"),
        ("21.42", "unsigned-floating"),
        ("-21.42", "negative-floating"),
        ("21/42", "unsigned-fraction"),
        ("-21/42", "negative-fraction"),
    )
)


@mark.parametrize(("numeric",), numerics)
def test_numeric_parser(numeric):
    parsed = pr.parse(numeric)
    assert str(parsed.value) == str(parsed)


expressions_simple = (
    ("42",  "numeric_integral"),
    ("21.42","numeric_floating"),
    ("1/2", "numeric_fraction"),
    ("-+>", "symbol_glyph"),
    ("add", "symbol_names"),
    (":-+>", "atom_glyphs"),
    (":TRUE", "atom_names"),
    ("\"hello, world\"", "string"),
    ("(+ 42 42)", "s_expression"),
    ("[add 42 42]", "vector"),
)


quoted_single = (
    param(f"'{quoted}", id=f"{identity}-single")
    for quoted, identity in expressions_simple
)

quoted_multi = (
    param(f"''{quoted}", id=f"{identity}-multi")
    for quoted, identity in expressions_simple
)


@mark.parametrize(("quoted",), (*quoted_single, *quoted_multi))
def test_quoted(quoted):
    assert quoted == str(pr.parse(quoted))


s_expressions = (
    param(s_expression, id=identity)
    for s_expression, identity in (
        ("(+ 42 42)", "flat"),
        ("(+ (+ 42 42) (+ 42 42))", "nested"),
    )
)


@mark.parametrize(("s_expression"), s_expressions)
def test_s_expression(s_expression):
    assert s_expression == str(pr.parse(s_expression))


vectors = [
    param(vector, id=identity)
    for vector, identity in (
        ("[add 42 42]", "flat"),
        ("[add [add 42 42] [add 42 42]]", "nested")
    )
]


@mark.parametrize(("vector",), vectors)
def test_vector(vector):
    assert vector == str(pr.parse(vector))


norm_failures = (
    param(text, error, id=f"'{text}'-{error.__name__}")
    for text, error in (
        ("(+ 1 2", pr.MissingClosing),
        ("[1 2 3", pr.MissingClosing),
        ("\"    ", pr.UnexpectedInput),
    )
)


@mark.parametrize(("text", "error"), norm_failures)
def test_parser_parse_raises(text, error):
    with raises(error):
        pr.parse(text)
