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


def test_function_call(env, mocker):
    fn = mocker.Mock(return_value=mocker.Mock())
    function = Function("function-call-test", fn, False)

    sym = Symbol("x")
    num = Numeric(21)

    env["x"] = Numeric(21)

    assert function.call(env, sym, num) == fn.return_value
    fn.assert_called_once_with(env, num, num)


def test_function_call_defer(env, mocker):
    fn = mocker.Mock(return_value=mocker.Mock())
    function = Function("function-call-defer-test", fn, True)

    sym = Symbol("x")
    num = Numeric(42)

    function.call(env, sym, num)
    fn.assert_called_once_with(env, Quoted(sym), Quoted(num))


def test_function_call_env_override(env, mocker):
    fn = mocker.Mock(return_value=mocker.Mock())

    function = Function("function-call-env-override", fn, False)
    function.env = env

    sym = Numeric(42)

    function.call(Environment(), sym)
    fn.assert_called_once_with(env, sym)


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
