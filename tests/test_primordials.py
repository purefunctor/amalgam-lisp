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
)

from pytest import fixture, mark, param


@fixture
def env():
    return Environment(None, FUNCTIONS)


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


comps = (
    param(comp_func, comp_x, comp_y, comp_rslt, id=comp_iden)
    for comp_func, comp_x, comp_y, comp_rslt, comp_iden in (
        (_gt, Numeric(5), Numeric(4), Atom("TRUE"), "gt"),
        (_gt, Numeric(4), Numeric(5), Atom("FALSE"), "gt-complement"),
        (_lt, Numeric(4), Numeric(5), Atom("TRUE"), "lt"),
        (_lt, Numeric(5), Numeric(4), Atom("FALSE"), "lt-complement"),
        (_eq, Numeric(5), Numeric(5), Atom("TRUE"), "eq"),
        (_eq, Numeric(4), Numeric(5), Atom("FALSE"), "eq-complement"),
        (_ne, Numeric(4), Numeric(5), Atom("TRUE"), "ne"),
        (_ne, Numeric(5), Numeric(5), Atom("FALSE"), "ne-complement"),
        (_ge, Numeric(5), Numeric(4), Atom("TRUE"), "ge"),
        (_ge, Numeric(4), Numeric(5), Atom("FALSE"), "ge-complement"),
        (_le, Numeric(4), Numeric(5), Atom("TRUE"), "le"),
        (_le, Numeric(5), Numeric(4), Atom("FALSE"), "le-complement"),
        (_ge, Numeric(5), Numeric(5), Atom("TRUE"), "ge-equality"),
        (_le, Numeric(5), Numeric(5), Atom("TRUE"), "le-equality")
    )
)


@mark.parametrize(("comp_func", "comp_x", "comp_y", "comp_rslt"), comps)
def test_comp(env, comp_func, comp_x, comp_y, comp_rslt):
    assert comp_func(env, comp_x, comp_y) == comp_rslt
