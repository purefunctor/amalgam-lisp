from amalgam.parser import s_expression


def test_s_expression_arithmetic_simple():
    assert s_expression.parse("(+ 21 42)") == ["(", "+", "21", "42", ")"]


def test_s_expression_arithmetic_nested():
    assert s_expression.parse("(+ 21 42 (+ 21 42))") == ["(", "+", "21", "42", ["(", "+", "21", "42", ")"], ")"]
