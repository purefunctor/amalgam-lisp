from fractions import Fraction
from functools import partial
from itertools import chain
from pathlib import Path
import sys
from typing import Callable, Dict, TypeVar, Union

from amalgam.amalgams import (
    create_fn,
    Amalgam,
    Atom,
    Function,
    Numeric,
    Quoted,
    String,
    Symbol,
    Vector,
)
from amalgam.environment import Environment


FUNCTIONS: Dict[str, Function] = {}


T = TypeVar("T", bound=Amalgam)


def _make_function(
    name: str,
    func: Callable[..., T] = None,
    defer: bool = False
) -> Union[partial, Callable[..., T]]:
    """
    Transforms a given function `func` into a `Function`
    and stores it inside of the `FUNCTIONS` mapping.
    """

    if func is None:
        return partial(_make_function, name, defer=defer)

    FUNCTIONS[name] = Function(name, func, defer)

    return func


@_make_function("+")
def _add(_env: Environment, *nums: Numeric) -> Numeric:
    return Numeric(sum(num.value for num in nums))


@_make_function("-")
def _sub(_env: Environment, *nums: Numeric) -> Numeric:
    x, *ns = (num.value for num in nums)
    y: Union[float, Fraction] = 0
    for n in ns:
        y += n
    return Numeric(x - y)


@_make_function("*")
def _mul(_env: Environment, *nums: Numeric) -> Numeric:
    prod: Union[float, Fraction] = 1
    for num in nums:
        prod *= num.value
    return Numeric(prod)


@_make_function("/")
def _div(_env: Environment, *nums: Numeric) -> Numeric:
    x, *ns = (num.value for num in nums)
    y: Union[float, Fraction] = 1
    for n in ns:
        y *= n
    return Numeric(x / y)


@_make_function("setn", defer=True)
def _setn(env: Environment, name: Quoted[Symbol], amalgam: Quoted[Amalgam]) -> Amalgam:
    env[name.value.value] = amalgam.value.evaluate(env)
    return env[name.value.value]


@_make_function("fn", defer=True)
def _fn(
    _env: Environment, args: Quoted[Vector[Symbol]], body: Quoted[Amalgam],
) -> Function:
    return create_fn("~lambda~", [arg.value for arg in args.value.vals], body.value)


@_make_function("mkfn", defer=True)
def _mkfn(
    env: Environment,
    name: Quoted[Symbol],
    args: Quoted[Vector[Symbol]],
    body: Quoted[Amalgam],
) -> Amalgam:
    return _setn(env, name, Quoted(_fn(env, args, body).with_name(name.value.value)))


@_make_function("bool")
def _bool(_env: Environment, expr: Amalgam) -> Atom:
    if expr == String(""):
        return Atom("FALSE")
    elif expr == Numeric(0):
        return Atom("FALSE")
    elif expr == Vector():
        return Atom("FALSE")
    elif expr == Atom("FALSE"):
        return Atom("FALSE")
    elif expr == Atom("NIL"):
        return Atom("FALSE")
    return Atom("TRUE")


@_make_function(">")
def _gt(_env: Environment, x: Amalgam, y: Amalgam) -> Atom:
    if x > y:  # type: ignore
        return Atom("TRUE")
    return Atom("FALSE")


@_make_function("<")
def _lt(_env: Environment, x: Amalgam, y: Amalgam) -> Atom:
    if x < y:  # type: ignore
        return Atom("TRUE")
    return Atom("FALSE")


@_make_function("=")
def _eq(_env: Environment, x: Amalgam, y: Amalgam) -> Atom:
    if x == y:
        return Atom("TRUE")
    return Atom("FALSE")


@_make_function("/=")
def _ne(_env: Environment, x: Amalgam, y: Amalgam) -> Atom:
    if x != y:
        return Atom("TRUE")
    return Atom("FALSE")


@_make_function(">=")
def _ge(env: Environment, x: Amalgam, y: Amalgam) -> Atom:
    if x >= y:  # type: ignore
        return Atom("TRUE")
    return Atom("FALSE")


@_make_function("<=")
def _le(env: Environment, x: Amalgam, y: Amalgam) -> Atom:
    if x <= y:  # type: ignore
        return Atom("TRUE")
    return Atom("FALSE")


@_make_function("not")
def _not(_env: Environment, expr: Amalgam) -> Atom:
    if _bool(_env, expr) == Atom("TRUE"):
        return Atom("FALSE")
    return Atom("TRUE")


@_make_function("and", defer=True)
def _and(env: Environment, *qexprs: Quoted[Amalgam]) -> Atom:
    for qexpr in qexprs:
        cond = _bool(env, qexpr.value.evaluate(env))
        if cond == Atom("FALSE"):
            return cond
    return Atom("TRUE")


@_make_function("or", defer=True)
def _or(env: Environment, *qexprs: Quoted[Amalgam]) -> Atom:
    for qexpr in qexprs:
        cond = _bool(env, qexpr.value.evaluate(env))
        if cond == Atom("TRUE"):
            return cond
    return Atom("FALSE")


@_make_function("if", defer=True)
def _if(
    env: Environment,
    qcond: Quoted[Amalgam],
    qthen: Quoted[Amalgam],
    qelse: Quoted[Amalgam],
) -> Amalgam:
    cond = _bool(env, qcond.value.evaluate(env))
    if cond == Atom("TRUE"):
        return qthen.value.evaluate(env)
    return qelse.value.evaluate(env)


@_make_function("cond", defer=True)
def _cond(env: Environment, *qpairs: Quoted[Vector[Amalgam]]) -> Amalgam:
    for qpair in qpairs:
        pred, expr = qpair.value.vals
        if _bool(env, pred.evaluate(env)) == Atom("TRUE"):
            return expr.evaluate(env)
    return Atom("NIL")


@_make_function("exit")
def _exit(env: Environment, exit_code: Numeric = Numeric(0)) -> Amalgam:
    print("Goodbye.")
    sys.exit(int(exit_code.value))


@_make_function("print")
def _print(_env: Environment, amalgam: Amalgam) -> Amalgam:
    print(amalgam)
    return amalgam


@_make_function("putstrln")
def _putstrln(_env: Environment, string: String) -> String:
    if not isinstance(string, String):
        raise TypeError("putstrln only accepts a string")
    print(string.value)
    return string


@_make_function("do", defer=True)
def _do(env: Environment, *qexprs: Quoted[Amalgam]) -> Amalgam:
    accumulator = Atom("NIL")
    for qexpr in qexprs:
        accumulator = qexpr.value.evaluate(env)
    return accumulator


@_make_function("require")
def _require(env: Environment, module_name: String) -> Atom:
    module_path = Path(module_name.value).absolute()
    with module_path.open("r", encoding="UTF-8") as f:
        env["~engine~"].parse_and_run(f.read())
    return Atom("NIL")


@_make_function("concat")
def _concat(_env: Environment, *strings: String) -> String:
    return String("".join(string.value for string in strings))


@_make_function("merge")
def _merge(_env: Environment, *vectors: Vector) -> Vector:
    return Vector(*chain.from_iterable(vector.vals for vector in vectors))


@_make_function("slice")
def _slice(
    _env: Environment,
    vector: Vector,
    start: Numeric,
    stop: Numeric,
    step: Numeric = Numeric(1),
) -> Vector:
    return Vector(*vector.vals[start.value:stop.value:step.value])


@_make_function("sliceup")
def _sliceup(
    _env: Environment,
    vector: Vector,
    start: Numeric,
    stop: Numeric,
    update: Vector,
) -> Vector:
    vals = list(vector.vals)
    vals[start.value:stop.value] = update.vals
    return Vector(*vals)


@_make_function("at")
def _at(_env: Environment, vector: Vector, index: Numeric) -> Amalgam:
    return vector.vals[index.value]
