from amalgam.amalgams import (
    create_fn,
    Atom,
    Environment,
    Function,
    Numeric,
    Quoted,
    SExpression,
    String,
    Symbol,
    Vector,
)

from amalgam.primordials import FUNCTIONS

from pytest import fixture, mark, param

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


@fixture
def env():
    return Environment(FUNCTIONS)


amalgams = (
    param(amalgam, id=amalgam.__class__.__name__)
    for amalgam in (
        Atom("self-eval"),
        String("self-eval"),
        Numeric(42),
        Quoted(Numeric(42)),
        Function("self-eval", lambda *_: None),
    )
)


@mark.parametrize(("amalgam",), amalgams)
def test_amalgam_evaluates_to_self(env, amalgam):
    assert amalgam.evaluate(env) == amalgam


def test_symbol_evaluate(env):
    env_ = env.env_push()

    s = Symbol("+").evaluate(env_)
    with env_.search_at(depth=-1):
        e = env["+"]

    assert s == e


def test_vector_evaluate(env):
    vector = Vector(Symbol("+"), Numeric(42))
    assert vector.evaluate(env) == Vector(env["+"], Numeric(42))


def test_s_expression_evaluate(env):
    sexpr = SExpression(Symbol("+"), Numeric(21), Numeric(21))
    assert sexpr.evaluate(env) == Numeric(42)


def test_function_bind(env):
    function = Function("function-bind-test", lambda _e, *_a: Vector(*_a), False)

    function_bind_result = function.bind(env)

    assert function_bind_result == function
    assert function.env == env


def test_function_with_name():
    function = Function("function-with-name-test", lambda _e, *_a: Vector(*_a), False)
    new_name = "new-name"

    function_with_name_result = function.with_name(new_name)

    assert function_with_name_result == function
    assert function.name == new_name


def test_function_call_return(env):
    function = Function("call-return-test", lambda *_: Numeric(42), False)
    assert function.call(env) == Numeric(42)


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


def test_closure_fn(mocker, mock_environment, mock_fn):
    mock_fargs = mocker.MagicMock()
    mock_fargs.__iter__.return_value = (mocker.Mock(), mocker.Mock())

    mock_args = mocker.MagicMock()
    mock_args.__iter__.return_value = (mocker.Mock(), mocker.Mock())

    mock_fbody = MockAmalgam()
    mock_fbody_result = MockAmalgam()
    mock_fbody.evaluate.return_value = mock_fbody_result

    mock_child_environment = MockEnvironment()
    mock_environment.env_push.return_value = mock_child_environment

    mocker.patch("amalgam.amalgams.Function", mock_fn)
    create_fn(mocker.MagicMock(), mock_fargs, mock_fbody, mocker.MagicMock())
    _, closure_fn, _ = mock_fn.call_args[0]

    closure_fn_result = closure_fn(mock_environment, *mock_args)

    mock_environment.env_push.assert_called_once_with(dict(zip(mock_fargs, mock_args)))
    mock_fbody.evaluate.assert_called_once_with(mock_child_environment)
    mock_fbody_result.bind.assert_called_once_with(mock_child_environment)
    assert closure_fn_result == mock_fbody_result
