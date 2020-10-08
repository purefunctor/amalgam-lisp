from amalgam.amalgams import (
    create_fn,
    Environment,
    Function,
    Numeric,
    Quoted,
    SExpression,
    String,
    Symbol,
    Vector,
)

from tests.utils import (
    MockAmalgam,
    MockEnvironment,
)


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
    mock_v0 = MockAmalgam()
    mock_v1 = MockAmalgam()

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


def test_function_call_naive(mocker):
    mock_environment = MockEnvironment()
    mock_fn = mocker.MagicMock()
    mock_fn_result = mocker.MagicMock()
    mock_fn.return_value = mock_fn_result
    mock_a0 = MockAmalgam()
    mock_a1 = MockAmalgam()

    function = Function("naive-call-test", mock_fn)
    function_call_result = function.call(mock_environment, mock_a0, mock_a1)

    mock_a0.evaluate.assert_called_once_with(mock_environment)
    mock_a1.evaluate.assert_called_once_with(mock_environment)
    mock_fn.assert_called_once_with(mock_environment, mock_a0, mock_a1)
    assert function_call_result == mock_fn_result
