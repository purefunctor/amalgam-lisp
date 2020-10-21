from amalgam.amalgams import (
    create_fn,
    Atom,
    Function,
    Numeric,
    Quoted,
    SExpression,
    String,
    Symbol,
    Vector,
)
from amalgam.environment import Environment
from amalgam.primordials import FUNCTIONS

from pytest import fixture, mark, param


@fixture
def env():
    return Environment(None, FUNCTIONS)


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
    env_ = env.env_push({})

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

    function.call(Environment(None, {}), sym)
    fn.assert_called_once_with(env, sym)


def test_create_fn_simple(env):
    function = create_fn(
        "create_fn-simple-test",
        ["x", "y"],
        Vector(Symbol("x"), Symbol("y")),
        False,
    )

    _21 = Numeric(21)
    vec = Vector(_21, _21)

    assert function.name == "create_fn-simple-test"
    assert function.defer == False
    assert function.call(env, _21, _21) == vec


def test_create_fn_closure(env):
    function = create_fn(
        "create_fn-simple-closure",
        ["x"],
        create_fn(
            "~lambda~",
            ["y"],
            Vector(Symbol("x"), Symbol("y")),
            False,
        ),
        False
    )

    _21 = Numeric(21)
    vec = Vector(_21, _21)

    closure = function.call(env, _21)
    assert closure.name == "~lambda~"
    assert closure.env is not None
    assert closure.defer == False
    assert closure.call(env, _21) == vec
