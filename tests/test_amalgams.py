from amalgam.amalgams import (
    create_fn,
    Atom,
    Function,
    Internal,
    Located,
    Notification,
    Numeric,
    Quoted,
    SExpression,
    String,
    Symbol,
    Trace,
    Vector,
)
from amalgam.environment import Environment
from amalgam.primordials import FUNCTIONS

from pytest import fixture, mark, param, raises


@fixture
def env():
    return Environment(FUNCTIONS)


def test_located():
    located = Located()

    assert located.line_span == (-1, -1)
    assert located.column_span == (-1, -1)

    assert located.line == -1
    assert located.end_line == -1

    assert located.column == -1
    assert located.end_column == -1

    assert located.located_on(lines=(5, 5), columns=(10, 10)) == located

    assert located.line_span == (5, 5)
    assert located.column_span == (10, 10)

    assert located.line == 5
    assert located.end_line == 5

    assert located.column == 10
    assert located.end_column == 10


amalgams = (
    param(amalgam, id=amalgam.__class__.__name__)
    for amalgam in (
        Atom("self-eval"),
        String("self-eval"),
        Numeric(42),
        Quoted(Numeric(42)),
        Function("self-eval", lambda *_: None),
        Internal(42),
        Notification(),
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


def test_vector_mapping(env):
    v0 = Vector()
    assert v0.mapping == {}

    v1 = Vector(Numeric(42))
    assert v1.mapping == {}

    v2 = Vector(Symbol("+"), Numeric(42))
    assert v2.mapping == {}

    v3 = Vector(Atom("FOO"), Numeric(42))
    assert v3.mapping == {"FOO": Numeric(42)}

    v4 = Vector(Atom("FOO"), Numeric(42), Atom("BAR"), Numeric(42))
    assert v4.mapping == {"FOO": Numeric(42), "BAR": Numeric(42)}


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
    fn.assert_called_once_with(env, sym, num)


def test_function_call_contextual(env, mocker):
    fn = mocker.Mock()
    function = Function("function-call-contextual-test", fn, False, True)

    assert isinstance(function.call(env), Notification)

    function.in_context = True

    function.call(env)
    fn.assert_called_once_with(env)


def test_function_call_env_override(env, mocker):
    fn = mocker.Mock(return_value=mocker.Mock())

    function = Function("function-call-env-override", fn, False)
    function.env = env

    sym = Numeric(42)

    function.call(Environment(), sym)
    fn.assert_called_once_with(env, sym)


def test_notification(env):
    sym = Symbol("x")

    t0 = Trace(sym, env, "test-notification-0")
    t1 = Trace(sym, env, "test-notification-0")

    n = Notification()
    n.push(*t0)
    n.push(*t1)

    assert list(n) == [t1, t0]
    assert n.pop() == t1
    assert n.pop() == t0


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
