from amalgam.amalgams import (
    create_fn,
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
    MockAmalgam,
    MockEnvironment,
)


@fixture
def mock_environment():
    return MockEnvironment()


@fixture
def mock_fn(mocker):
    return mocker.MagicMock(return_value=mocker.MagicMock())


def test_string_evaluate(mock_environment):
    string = String("string-test")
    assert string.evaluate(mock_environment) == string


def test_numeric_evaluate(mock_environment):
    numeric = Numeric(42)
    assert numeric.evaluate(mock_environment) == numeric


def test_quoted_evaluate(mock_environment):
    quoted = Quoted(Symbol("quoted-test"))
    assert quoted.evaluate(mock_environment) == quoted


def test_symbol_evaluate(mocker, mock_environment):
    mock_amalgam_result = mocker.MagicMock()
    mock_environment.__getitem__.return_value = mock_amalgam_result
    mock_value = mocker.MagicMock()

    symbol_evaluate_result = Symbol(mock_value).evaluate(mock_environment)

    mock_environment.__getitem__.assert_called_once_with(mock_value)
    assert symbol_evaluate_result == mock_amalgam_result


def test_vector_evaluate(mocker, mock_environment):
    mock_v0 = MockAmalgam()
    mock_v1 = MockAmalgam()

    vector_evaluate_result = Vector(mock_v0, mock_v1).evaluate(mock_environment)

    mock_v0.evaluate.assert_called_once_with(mock_environment)
    mock_v1.evaluate.assert_called_once_with(mock_environment)
    assert vector_evaluate_result == Vector(mock_v0, mock_v1)


def test_s_expression_evaluate(mocker, mock_environment):
    mock_func = mocker.MagicMock()
    mock_func.evaluate.return_value = mock_func
    mock_func_result = mocker.MagicMock()
    mock_func.call.return_value = mock_func_result
    mock_args = (mocker.MagicMock(), mocker.MagicMock())

    sexpr_evaluate_result = SExpression(mock_func, *mock_args).evaluate(mock_environment)

    mock_func.evaluate.assert_called_once_with(mock_environment)
    mock_func.call.assert_called_once_with(mock_environment, *mock_args)
    assert sexpr_evaluate_result == mock_func_result


def test_function_bind(mock_environment):
    function = Function("function-bind-test", lambda _e, *_a: Vector(*_a), False)

    function_bind_result = function.bind(mock_environment)

    assert function_bind_result == function
    assert function.env == mock_environment


def test_function_evalulate(mock_environment):
    function = Function("function-evaluate-test", lambda _e, *_a: Vector(*_a), False)
    assert function.evaluate(mock_environment) == function


def test_function_with_name():
    function = Function("function-with-name-test", lambda _e, *_a: Vector(*_a), False)
    new_name = "new-name"

    function_with_name_result = function.with_name(new_name)

    assert function_with_name_result == function
    assert function.name == new_name


def test_function_call_return(mock_environment, mock_fn):
    function = Function("call-return-test", mock_fn)
    assert function.call(mock_environment, MockAmalgam()) == mock_fn.return_value


def test_function_call_naive(mock_environment, mock_fn):
    mock_ev = MockAmalgam()
    mock_a0 = MockAmalgam(evaluate=mock_ev)
    mock_a1 = MockAmalgam()

    function = Function("naive-call-test", mock_fn)
    function.call(mock_environment, mock_a0, mock_a1)

    mock_a0.evaluate.assert_called_once_with(mock_environment)
    mock_a1.evaluate.assert_called_once_with(mock_environment)
    mock_fn.assert_called_once_with(mock_environment, mock_ev, mock_a1)


def test_function_call_defer(mocker, mock_environment, mock_fn):
    mock_a0 = MockAmalgam()
    mock_a1 = MockAmalgam()
    mock_q0 = MockAmalgam()
    mock_q1 = MockAmalgam()

    mock_Quoted = mocker.Mock(side_effect=(mock_q0, mock_q1))
    mocker.patch("amalgam.amalgams.Quoted", mock_Quoted)

    function = Function("defer-call-test", mock_fn, defer=True)
    function.call(mock_environment, mock_a0, mock_a1)

    assert mock_Quoted.mock_calls == [mocker.call(mock_a0), mocker.call(mock_a1)]
    mock_fn.assert_called_once_with(mock_environment, mock_q0, mock_q1)


def test_function_call_env_override(mock_environment, mock_fn):
    mock_ag = MockAmalgam()

    function = Function("env-override-test", mock_fn)
    function.env = mock_environment
    function.call(MockEnvironment(), mock_ag)

    mock_fn.assert_called_once_with(mock_environment, mock_ag)


def test_create_fn(mocker, mock_fn):
    mock_fname = mocker.MagicMock()
    mock_defer = mocker.MagicMock()

    mocker.patch("amalgam.amalgams.Function", mock_fn)

    create_fn_result = create_fn(mock_fname, mocker.MagicMock(), mocker.MagicMock(), mock_defer)

    mock_fn.assert_called_once_with(mock_fname, mocker.ANY, mock_defer)
    assert create_fn_result == mock_fn.return_value
