from fractions import Fraction

from amalgam.amalgams import (
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
from amalgam.primordials import (
    FUNCTIONS,
    _add,
    _sub,
    _mul,
    _div,
    _setn,
    _fn,
    _mkfn,
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
)

from pytest import fixture, mark, param, raises


@fixture
def env():
    return Environment(None, FUNCTIONS.copy())


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

    _setn_result = _setn(env, Quoted(name), Quoted(amalgam))

    assert env.iget("name") == amalgam
    assert _setn_result == amalgam


def test_fn(env):
    args = Vector(Symbol("x"), Symbol("y"))
    body = SExpression(Symbol("+"), Symbol("x"), Symbol("y"))

    _fn_result = _fn(env, Quoted(args), Quoted(body))

    assert _fn_result.fn(env, Numeric(21), Numeric(21)) == Numeric(42)


def test_mkfn(env):
    name = Symbol("name")
    args = Vector(Symbol("x"), Symbol("y"))
    body = SExpression(Symbol("+"), Symbol("x"), Symbol("y"))

    _mkfn_result = _mkfn(env, Quoted(name), Quoted(args), Quoted(body))

    assert env.iget("name") == _mkfn_result
    assert _mkfn_result.fn(env, Numeric(21), Numeric(21)) == Numeric(42)


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

    _and_result = _and(env, *map(Quoted, exprs))

    assert _and_result == Atom("FALSE")
    assert env.ihas("x")
    assert not env.ihas("y")


def test_and_default(env):
    assert _and(env, Quoted(Atom("TRUE"))) == Atom("TRUE")


def test_or(env):
    exprs = (
        SExpression(Symbol("setn"), Symbol("x"), Atom("FALSE")),
        Atom("TRUE"),
        SExpression(Symbol("setn"), Symbol("y"), Atom("FALSE")),
    )

    _or_result = _or(env, *map(Quoted, exprs))

    assert _or_result == Atom("TRUE")
    assert env.ihas("x")
    assert not env.ihas("y")


def test_or_default(env):
    assert _or(env, Quoted(Atom("FALSE"))) == Atom("FALSE")


def test_if_then(env):
    cond = SExpression(Symbol("setn"), Symbol("w"), Atom("TRUE"))
    then_else = (
        SExpression(Symbol("setn"), Symbol("x"), Atom("THEN")),
        SExpression(Symbol("setn"), Symbol("y"), Atom("ELSE")),
    )

    _if_result_then = _if(env, Quoted(cond), *map(Quoted, then_else))

    assert _if_result_then == Atom("THEN")
    assert env.ihas("w")
    assert env.ihas("x")
    assert not env.ihas("y")


def test_if_else(env):
    cond = SExpression(Symbol("setn"), Symbol("w"), Atom("FALSE"))
    then_else = (
        SExpression(Symbol("setn"), Symbol("x"), Atom("THEN")),
        SExpression(Symbol("setn"), Symbol("y"), Atom("ELSE")),
    )

    _if_result_else = _if(env, Quoted(cond), *map(Quoted, then_else))

    assert _if_result_else == Atom("ELSE")
    assert env.ihas("w")
    assert not env.ihas("x")
    assert env.ihas("y")


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
    pairs = (Quoted(Vector(*pair)) for pair in zip(predicates, values))

    _cond_result = _cond(env, *pairs)

    assert _cond_result == Atom("SECOND")
    assert env.ihas("u")
    assert env.ihas("v")
    assert not env.ihas("w")
    assert not env.ihas("x")
    assert env.ihas("y")
    assert not env.ihas("z")


def test_cond_nil(env):
    assert _cond(env, Quoted(Vector(Atom("FALSE"), Atom("FALSE")))) == Atom("NIL")


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

    assert _do(env, *map(Quoted, exprs)) == Numeric(42)
    assert capsys.readouterr().out == "42\n"
