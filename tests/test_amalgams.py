from fractions import Fraction
import re
from typing import Any

from amalgam.amalgams import (
    create_fn,
    Amalgam,
    Environment,
    Function,
    Numeric,
    Quoted,
    SExpression,
    String,
    Symbol,
    Vector,
)

from pytest import fixture

from tests.utils import (
    MockEnvironment,
)

@fixture
def numerics():
    return Numeric(21), Numeric(21.42), Numeric(Fraction(21, 42))


@fixture
def strings():
    return String(""), String("\n\t"), String("foo-bar-baz")


@fixture
def num():
    return Numeric(42)


@fixture
def fresh_env():
    return Environment()


@fixture
def store_env():
    env = Environment()

    def plus_func(_environment: Environment, *numbers: Numeric) -> Numeric:
        return Numeric(sum(number.value for number in numbers))

    def fn_func(
        _env: Environment, args: Quoted[Vector[Symbol]], body: Quoted[Amalgam],
    ) -> Function:
        return create_fn("<lambda>", [arg.value for arg in args.value.vals], body.value)

    def defun_func(
        env: Environment, name: Quoted[String], args: Quoted[Vector[Symbol]], body: Quoted[Amalgam]
    ) -> Function:
        env[name.value.value] = fn_func(env, args, body)
        return env[name.value.value]

    def prog_func(env: Environment, *expressions: SExpression) -> Vector[Amalgam]:
        return Vector(*(expression.evaluate(env) for expression in expressions))

    env["+"] = Function("+", plus_func)
    env["fn"] = Function("fn", fn_func, defer=True)
    env["defun"] = Function("defun", defun_func, defer=True)
    env["prog"] = Function("prog", prog_func)

    env["z"] = Numeric(42)

    return env


def test_string_evaluate():
    string = String("string-test")
    assert string.evaluate(Environment()) == string


def test_numeric_evaluate():
    numeric = Numeric(42)
    assert numeric.evaluate(Environment()) == numeric


def test_quoted_evaluate():
    quoted = Quoted(Symbol("quoted-test"))
    assert quoted.evaluate(Environment()) == quoted


def test_symbol_evaluate(mocker):
    mock_environment = MockEnvironment()
    mock_amalgam_result = mocker.MagicMock()
    mock_environment.__getitem__.return_value = mock_amalgam_result
    mock_value = mocker.MagicMock()

    symbol_evaluate_result = Symbol(mock_value).evaluate(mock_environment)

    mock_environment.__getitem__.assert_called_once_with(mock_value)
    assert symbol_evaluate_result == mock_amalgam_result


def test_vector_evaluate(mocker):
    mock_environment = MockEnvironment()
    mock_v0 = mocker.MagicMock()
    mock_v1 = mocker.MagicMock()
    mock_v0.evaluate.return_value = mock_v0
    mock_v1.evaluate.return_value = mock_v1

    vector_evaluate_result = Vector(mock_v0, mock_v1).evaluate(mock_environment)

    mock_v0.evaluate.assert_called_once_with(mock_environment)
    mock_v1.evaluate.assert_called_once_with(mock_environment)
    assert vector_evaluate_result == Vector(mock_v0, mock_v1)


def test_s_expression_evaluate(mocker):
    mock_environment = MockEnvironment()

    mock_func = mocker.MagicMock()
    mock_func.evaluate.return_value = mock_func
    mock_func_result = mocker.MagicMock()
    mock_func.call.return_value = mock_func_result
    mock_args = (mocker.MagicMock(), mocker.MagicMock())

    sexpr_evaluate_result = SExpression(mock_func, *mock_args).evaluate(mock_environment)

    mock_func.evaluate.assert_called_once_with(mock_environment)
    mock_func.call.assert_called_once_with(mock_environment, *mock_args)
    assert sexpr_evaluate_result == mock_func_result


def test_function_bind():
    environment = Environment()
    function = Function("function-bind-test", lambda _e, *_a: Vector(*_a), False)

    function_bind_result = function.bind(environment)

    assert function_bind_result == function
    assert function.env == environment


def test_function_evalulate():
    function = Function("function-evaluate-test", lambda _e, *_a: Vector(*_a), False)
    assert function.evaluate(Environment()) == function


def test_function_with_name():
    function = Function("function-with-name-test", lambda _e, *_a: Vector(*_a), False)
    new_name = "new-name"

    function_with_name_result = function.with_name(new_name)

    assert function_with_name_result == function
    assert function.name == new_name


def test_function_evaluate_literal(num, fresh_env):
    fnc = create_fn("literal-test", "_x", num)
    assert fnc.call(fresh_env, num).value == num.value


def test_function_evaluate_symbol_global(num, fresh_env):
    fresh_env["x"] = num
    fnc = create_fn("global-test", "", Symbol("x"))
    assert fnc.call(fresh_env).value == num.value


def test_function_evaluate_symbol_local(num, fresh_env):
    fresh_env["x"] = String("fail")
    fnc = create_fn("local-test", "x", Symbol("x"))
    assert fnc.call(fresh_env, num).value == num.value


def test_function_evaluate_symbol_closure(num, fresh_env):
    fnc = create_fn("closure-test", "x", create_fn("inner", "y", Symbol("x")))
    assert fnc.call(fresh_env, num).call(fresh_env, num).value == num.value
