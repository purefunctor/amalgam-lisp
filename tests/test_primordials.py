from fractions import Fraction

from amalgam.amalgams import (
    Atom,
    Failure,
    FailureStack,
    Function,
    Numeric,
    Quoted,
    SExpression,
    String,
    Symbol,
    Vector,
)
from amalgam.engine import Engine
from amalgam.environment import Environment
from amalgam.primordials import (
    _add,
    _sub,
    _mul,
    _div,
    _setn,
    _fn,
    _mkfn,
    _let,
    _bool,
    _gt,
    _lt,
    _eq,
    _ne,
    _ge,
    _le,
    _not,
    _and,
    _or,
    _if,
    _cond,
    _exit,
    _print,
    _putstrln,
    _do,
    _concat,
    _merge,
    _slice,
    _at,
    _len,
    _cons,
    _snoc,
    _remove,
    _is_map,
    _map_in,
    _map_at,
    _map_up,
    _when,
    _eval,
    _unquote,
    _setr,
    _macro,
)

from pytest import fixture, mark, param, raises


@fixture
def env():
    return Engine().environment


arithmetics = (
    param(
        arith_fn,
        arith_nm,
        arith_rs,
        id=f"({arith_op} {' '.join(map(str, arith_nm))})"
    )
    for arith_fn, arith_op, arith_nm, arith_rs in (
        (_add, "+", (1, 2), 1 + 2),
        (_add, "+", (1, 2, 3), 1 + 2 + 3),
        (_sub, "-", (5, 3), 5 - 3),
        (_sub, "-", (3, 5, 3), 3 - (5 + 3)),
        (_mul, "*", (2, 2), 2 * 2),
        (_mul, "*", (2, 2, 2), 2 * 2 * 2),
        (_div, "/", (4, 2), 4 / 2),
        (_div, "/", (6, 2, 3), 6 / (2 * 3)),
    )
)


@mark.parametrize(("arith_fn", "arith_nm", "arith_rs"), arithmetics)
def test_arithmetic_function(arith_fn, arith_nm, arith_rs):
    assert arith_fn(Environment(), *map(Numeric, arith_nm)).value == arith_rs


def test_setn(env):
    name = Symbol("name")
    amalgam = String("string")

    _setn_result = _setn(env, name, amalgam)

    assert env["name"] == amalgam
    assert _setn_result == amalgam


def test_setn_fail(env):
    name = Symbol("name")
    amalgam = Symbol("x")

    with raises(FailureStack) as f:
        _setn(env, name, amalgam)

    assert list(f.value.unpacked_failures) == [
        (amalgam, env, "unbound symbol"),
    ]


def test_fn(env):
    args = Vector(Symbol("x"), Symbol("y"))
    body = SExpression(Symbol("+"), Symbol("x"), Symbol("y"))

    _fn_result = _fn(env, args, body)

    assert _fn_result.fn(env, Numeric(21), Numeric(21)) == Numeric(42)


def test_fn_bound(env):
    cl_env = env.env_push()

    _fn_result = _fn(cl_env, Vector(), SExpression())

    assert _fn_result.env == cl_env


def test_mkfn(env):
    name = Symbol("name")
    args = Vector(Symbol("x"), Symbol("y"))
    body = SExpression(Symbol("+"), Symbol("x"), Symbol("y"))

    _mkfn_result = _mkfn(env, name, args, body)

    assert env["name"] == _mkfn_result
    assert _mkfn_result.fn(env, Numeric(21), Numeric(21)) == Numeric(42)


def test_let(env):
    env["z"] = Numeric(21)

    bindings = Vector(Vector(Symbol("x"), Numeric(21)), Vector(Symbol("y"), Symbol("z")))
    body = SExpression(Symbol("+"), Symbol("x"), Symbol("y"))

    _let_result = _let(env, bindings, body)

    assert _let_result == Numeric(42)
    assert "x" not in env
    assert "y" not in env


_let_failures = (
    param(_let_bindings, _let_exception, id=_let_name)
    for _let_bindings, _let_exception, _let_name in (
        (Vector(Symbol("x")), "not a pair", "not-a-vector"),
        (Vector(Vector(Numeric(42), Symbol("x"))), "not a symbol", "not-a-symbol"),
        (Vector(Vector(Symbol("x"))), "not a pair", "too-short"),
        (Vector(Vector(Symbol("x"), Symbol("y"), Symbol("z"))), "not a pair", "too-long"),
    )
)


@mark.parametrize(("bindings", "exception"), _let_failures)
def test_let_fails(env, bindings, exception):
    with raises((Failure, FailureStack), match=exception):
        _let(env, bindings, SExpression())


_t = Atom("TRUE")
_f = Atom("FALSE")

_truthy_falsy = (
    (String(""), _f, _t, "empty-string",),
    (String("a"), _t, _f, "non-empty-string"),
    (Numeric(0), _f, _t, "zero-value"),
    (Numeric(1), _t, _f, "non-zero-value"),
    (Vector(), _f, _t, "empty-vector"),
    (Vector(Numeric(1)), _t, _f, "non-empty-vector"),
    (Atom("FALSE"), _f, _t, "false-atom"),
    (Atom("TRUE"), _t, _f, "true-atom"),
    (Atom("NIL"),  _f, _t, "nil-atom"),
    (Atom("OTH"), _t, _f, "other-atom")
)

bools = (
    param(bool_expr, bool_rslt, id=bool_iden)
    for bool_expr, bool_rslt, _, bool_iden in _truthy_falsy
)


nots = (
    param(not_expr, not_rlst, id=not_iden)
    for not_expr, _, not_rlst, not_iden in _truthy_falsy
)


@mark.parametrize(("bool_expr", "bool_rslt"), bools)
def test_bool(env, bool_expr, bool_rslt):
    assert _bool(env, bool_expr) == bool_rslt


@mark.parametrize(("not_expr", "not_rslt"), nots)
def test_not(env, not_expr, not_rslt):
    return _not(env, not_expr) == not_rslt


_four = Numeric(4)
_five = Numeric(5)


comps = (
    param(comp_func, comp_x, comp_y, comp_rslt, id=comp_iden)
    for comp_func, comp_x, comp_y, comp_rslt, comp_iden in (
        (_gt, _five, _four, _t, "gt"),
        (_lt, _four, _five, _t, "lt"),
        (_eq, _five, _five, _t, "eq"),
        (_ne, _four, _five, _t, "ne"),
        (_ge, _five, _four, _t, "ge"),
        (_le, _four, _five, _t, "le"),
        (_gt, _four, _five, _f, "gt-complement"),
        (_lt, _five, _four, _f, "lt-complement"),
        (_eq, _four, _five, _f, "eq-complement"),
        (_ne, _five, _five, _f, "ne-complement"),
        (_ge, _four, _five, _f, "ge-complement"),
        (_le, _five, _four, _f, "le-complement"),
        (_ge, _five, _five, _t, "ge-equality"),
        (_le, _five, _five, _t, "le-equality")
    )
)


@mark.parametrize(("comp_func", "comp_x", "comp_y", "comp_rslt"), comps)
def test_comp(env, comp_func, comp_x, comp_y, comp_rslt):
    assert comp_func(env, comp_x, comp_y) == comp_rslt


def test_and(env):
    exprs = (
        SExpression(Symbol("setn"), Symbol("x"), Atom("TRUE")),
        Atom("FALSE"),
        SExpression(Symbol("setn"), Symbol("y"), Atom("TRUE")),
    )

    _and_result = _and(env, *exprs)

    assert _and_result == Atom("FALSE")
    assert "x" in env
    assert "y" not in env


def test_and_default(env):
    assert _and(env, Quoted(Atom("TRUE"))) == Atom("TRUE")


def test_or(env):
    exprs = (
        SExpression(Symbol("setn"), Symbol("x"), Atom("FALSE")),
        Atom("TRUE"),
        SExpression(Symbol("setn"), Symbol("y"), Atom("FALSE")),
    )

    _or_result = _or(env, *exprs)

    assert _or_result == Atom("TRUE")
    assert "x" in env
    assert "y" not in env


def test_or_default(env):
    assert _or(env, Atom("FALSE")) == Atom("FALSE")


def test_if_then(env):
    cond = SExpression(Symbol("setn"), Symbol("w"), Atom("TRUE"))
    then_else = (
        SExpression(Symbol("setn"), Symbol("x"), Atom("THEN")),
        SExpression(Symbol("setn"), Symbol("y"), Atom("ELSE")),
    )

    _if_result_then = _if(env, cond, *then_else)

    assert _if_result_then == Atom("THEN")
    assert "w" in env
    assert "x" in env
    assert "y" not in env


def test_if_else(env):
    cond = SExpression(Symbol("setn"), Symbol("w"), Atom("FALSE"))
    then_else = (
        SExpression(Symbol("setn"), Symbol("x"), Atom("THEN")),
        SExpression(Symbol("setn"), Symbol("y"), Atom("ELSE")),
    )

    _if_result_else = _if(env, cond, *then_else)

    assert _if_result_else == Atom("ELSE")
    assert "w" in env
    assert "x" not in env
    assert "y" in env


def test_cond(env):
    predicates = (
        SExpression(Symbol("setn"), Symbol("u"), Atom("FALSE")),
        SExpression(Symbol("setn"), Symbol("v"), Atom("TRUE")),
        SExpression(Symbol("setn"), Symbol("w"), Atom("FALSE")),
    )
    values = (
        SExpression(Symbol("setn"), Symbol("x"), Atom("FIRST")),
        SExpression(Symbol("setn"), Symbol("y"), Atom("SECOND")),
        SExpression(Symbol("setn"), Symbol("z"), Atom("THIRD")),
    )
    pairs = (Vector(*pair) for pair in zip(predicates, values))

    _cond_result = _cond(env, *pairs)

    assert _cond_result == Atom("SECOND")
    assert "u" in env
    assert "v" in env
    assert "w" not in env
    assert "x" not in env
    assert "y" in env
    assert "z" not in env


def test_cond_nil(env):
    assert _cond(env, Vector(Atom("FALSE"), Atom("FALSE"))) == Atom("NIL")


exits = (
    param(exit_status, id=exit_name)
    for exit_status, exit_name in (
        (0, "integer-zero"),
        (1, "integer-non-zero"),
        (0.0, "floating-zero"),
        (1.0, "floating-non-zero"),
        (Fraction(0, 1), "fraction-zero"),
        (Fraction(1, 1), "fraction-non-zero"),
    )
)


@mark.parametrize(("exit_status"), exits)
def test_exit(capsys, env, exit_status):
    with raises(SystemExit, match=f"{int(exit_status)}"):
        _exit(env, Numeric(exit_status))
    capsys.readouterr().out == "Goodbye.\n"


def test_print(capsys, env):
    string = String("hello, world")
    qvector = Quoted(Vector(Symbol("x"), Symbol("y")))

    assert _print(env, string) == string
    assert _print(env, qvector) == qvector

    assert capsys.readouterr().out == (
        f"\"hello, world\"\n"
        f"'[x y]\n"
    )


def test_putstrln(capsys, env):
    string = String("hello, world")
    qvector = Quoted(Vector(Symbol("x"), Symbol("y")))

    assert _putstrln(env, string) == string

    with raises(TypeError):
        _putstrln(env, qvector)

    assert capsys.readouterr().out == "hello, world\n"


def test_do(capsys, env):
    exprs = (
        SExpression(Symbol("setn"), Symbol("x"), Numeric(21)),
        SExpression(Symbol("setn"), Symbol("y"), Numeric(21)),
        SExpression(
            Symbol("print"),
            SExpression(
                Symbol("+"), Symbol("x"), Symbol("y"),
            )
        )
    )

    assert _do(env, *exprs) == Numeric(42)
    assert capsys.readouterr().out == "42\n"


def test_concat(env):
    s0 = String("hello")
    s1 = String("world")
    assert _concat(env, s0, s1) == String(s0.value + s1.value)


def test_merge(env):
    v0 = Vector(Atom("foo"), Numeric(21))
    v1 = Vector(Atom("bar"), Numeric(42))
    v2 = Vector(Numeric(63), Numeric(84))

    m0 = _merge(env, v0, v1)
    m1 = _merge(env, v0, v2)

    assert m0.vals == v0.vals + v1.vals
    assert m0.mapping == {**v0.mapping, **v1.mapping}

    assert m1.vals == v0.vals + v2.vals
    assert m1.mapping == {}


def test_slice(env):
    v0 = Vector(
        Atom("foo"), Numeric(21),
        Atom("bar"), Numeric(42),
        Atom("baz"), Numeric(63),
    )

    s0 = _slice(env, v0, Numeric(0), Numeric(4), Numeric(1))
    s1 = _slice(env, v0, Numeric(1), Numeric(5), Numeric(1))

    assert s0.vals == v0.vals[0:4:1]
    assert s0.mapping == {"foo": Numeric(21), "bar": Numeric(42)}

    assert s1.vals == v0.vals[1:5:1]
    assert s1.mapping == {}


def test_at(env):
    vector = Vector(Numeric(21), Numeric(42))
    assert _at(env, Numeric(1), vector) == Numeric(42)


def test_cons(env):
    v0 = Vector(Atom("foo"), Numeric(21))

    c0 = _cons(env, Numeric(42), v0)
    c1 = _cons(env, Atom("bar"), c0)

    assert c0 == Vector(Numeric(42), Atom("foo"), Numeric(21))
    assert c0.mapping == {}

    assert c1 == Vector(Atom("bar"), Numeric(42), Atom("foo"), Numeric(21))
    assert c1.mapping == {"bar": Numeric(42), "foo": Numeric(21)}


def test_snoc(env):
    v0 = Vector(Atom("foo"), Numeric(21))

    c0 = _snoc(env, v0, Atom("bar"))
    c1 = _snoc(env, c0, Numeric(42))

    assert c0 == Vector(Atom("foo"), Numeric(21), Atom("bar"))
    assert c0.mapping == {}

    assert c1 == Vector(Atom("foo"), Numeric(21), Atom("bar"), Numeric(42))
    assert c1.mapping == {"foo": Numeric(21), "bar": Numeric(42)}


def test_remove(env):
    v0 = Vector(Atom("foo"), Numeric(21), Atom("bar"), Numeric(42))

    r0 = _remove(env, Numeric(0), v0)
    r1 = _remove(env, Numeric(0), r0)

    assert r0.vals == v0.vals[1:]
    assert r0.mapping == {}

    assert r1.vals == v0.vals[2:]
    assert r1.mapping == {"bar": Numeric(42)}


def test_len(env):
    assert _len(env, Vector(Numeric(21), Numeric(42))) == Numeric(2)


@fixture
def vector_mapping():
    return Vector(Atom("foo"), Numeric(42))


@fixture
def vector_sequence():
    return Vector(Symbol("foo"), Numeric(42))


def test_is_map(env, vector_mapping, vector_sequence):
    assert _is_map(env, vector_mapping) == Atom("TRUE")
    assert _is_map(env, vector_sequence) == Atom("FALSE")


def test_map_in(env, vector_mapping, vector_sequence):
    assert _map_in(env, vector_mapping, Atom("foo")) == Atom("TRUE")
    assert _map_in(env, vector_mapping, Atom("bar")) == Atom("FALSE")

    with raises(ValueError):
        _map_in(env, vector_sequence, Atom("foo"))


def test_map_at(env, vector_mapping, vector_sequence):
    assert _map_at(env, vector_mapping, Atom("foo")) == Numeric(42)

    with raises(KeyError):
        _map_at(env, vector_mapping, Atom("bar"))

    with raises(ValueError):
        _map_at(env, vector_sequence, Atom("foo"))


def test_map_up(env, vector_mapping, vector_sequence):
    v0 = _map_up(env, vector_mapping, Atom("foo"), Numeric(21))
    v1 = _map_up(env, v0, Atom("bar"), Numeric(42))

    assert v1.vals == (Atom("foo"), Numeric(21), Atom("bar"), Numeric(42))
    assert v1.mapping == {"foo": Numeric(21), "bar": Numeric(42)}

    with raises(ValueError):
        _map_up(env, vector_sequence, Atom("baz"), Numeric(63))


def test_loop_return(env):
    env["x"] = Numeric(0)
    looped = SExpression(
        Symbol("loop"),
        SExpression(
            Symbol("if"),
            SExpression(
                Symbol("="),
                Symbol("x"),
                Numeric(10),
            ),
            SExpression(
                Symbol("return"),
                Numeric(42),
            ),
            Atom("NIL"),
        ),
        SExpression(
            Symbol("setn"),
            Symbol("x"),
            SExpression(
                Symbol("+"),
                Symbol("x"),
                Numeric(1),
            ),
        ),
    )

    assert looped.evaluate(env) == Numeric(42)
    assert env["x"] == Numeric(10)


def test_loop_break(env):
    broken = SExpression(
        Symbol("loop"),
        SExpression(Symbol("break")),
        SExpression(Symbol("setn"), Symbol("x"), Numeric(42)),
    )

    assert broken.evaluate(env) == Atom("NIL")
    assert "x" not in env


def test_loop_fatal(env):
    symbol = Symbol("x")
    sexpr = SExpression(Symbol("loop"), symbol)

    with raises(FailureStack) as f:
        sexpr.evaluate(env)

    assert list(f.value.unpacked_failures) == [
        (symbol, env, "unbound symbol"),
        (sexpr, env, "inherited"),
    ]


def test_when(env):
    cond = SExpression(
        Symbol("setn"), Symbol("x"), Atom("TRUE")
    )
    body = SExpression(
        Symbol("setn"), Symbol("y"), Numeric(42)
    )

    assert _when(env, cond, body) == Numeric(42)
    assert "x" in env
    assert "y" in env


def test_when_nil(env):
    assert _when(env, Atom("NIL"), Numeric(42)) == Atom("NIL")


def test_eval(env):
    env["x"] = Numeric(42)
    assert _eval(env, Symbol("x")) == Numeric(42)
    assert _eval(env, Quoted(Symbol("x"))) == Numeric(42)
    assert _eval(env, Quoted(Quoted(Symbol("x")))) == Quoted(Symbol("x"))


def test_unquote(env):
    q0 = Quoted(Numeric(42))
    assert _unquote(env, q0) == Numeric(42)

    with raises(TypeError):
        _unquote(env, Numeric(42))


def test_setr(env):
    env["r"] = Symbol("x")

    s0 = _setr(
        env,
        Symbol("r"),
        SExpression(Symbol("+"), Numeric(21), Numeric(21)),
    )

    assert s0 == Numeric(42)
    assert env["x"] == Numeric(42)

    with raises(TypeError):
        _setr(env, Symbol("x"), Numeric(21))


def test_macro(env):
    v0 = Vector(Symbol("x"), Symbol("y"))
    q0 = Quoted(Numeric(21))

    _macro_result = _macro(env, Symbol("macro-test"), v0, v0)

    assert env["macro-test"] == _macro_result
    assert _macro_result.defer == True
    assert _macro_result.fn(env, q0, q0) == Vector(q0, q0)


def test_macro_bound(env):
    cl_env = env.env_push()

    qv0 = Vector()

    _macro_result = _macro(cl_env, Symbol("macro-test"), qv0, qv0)

    assert _macro_result.env == cl_env
