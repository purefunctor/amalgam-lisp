from fractions import Fraction
from functools import partial, wraps
from itertools import chain
from pathlib import Path
import sys
from typing import (
    cast, Callable, Dict, List, NamedTuple, Sequence, TypeVar, Union
)

import amalgam.amalgams as am
import amalgam.engine as en
import amalgam.environment as ev


FUNCTIONS: Dict[str, am.Function] = {}


T = TypeVar("T", bound=am.Amalgam)


def _make_function(
    name: str,
    func: Callable[..., T] = None,
    defer: bool = False,
    contextual: bool = False,
    allows: Sequence[str] = None,
) -> Union[partial, Callable[..., T]]:
    """
    Transforms a given function `func` into a `Function`
    and stores it inside of the `FUNCTIONS` mapping.
    """

    if func is None:
        return partial(
            _make_function,
            name,
            defer=defer,
            contextual=contextual,
            allows=allows,
        )

    if allows is None:
        allows = []

    @wraps(func)
    def _func(env, *arguments, **keywords):
        with env.search_at(depth=-1):
            fns = [env[allow] for allow in allows]

        for fn in fns:
            cast(am.Function, fn).in_context = True

        result = func(env, *arguments, **keywords)

        for fn in fns:
            cast(am.Function, fn).in_context = False

        return result

    FUNCTIONS[name] = am.Function(name, _func, defer, contextual)

    return _func


@_make_function("+")
def _add(_env: ev.Environment, *nums: am.Numeric) -> am.Numeric:
    """Returns the sum of :data:`nums`."""
    return am.Numeric(sum(num.value for num in nums))


@_make_function("-")
def _sub(_env: ev.Environment, *nums: am.Numeric) -> am.Numeric:
    """
    Subtracts :data:`nums[0]` and the summation of :data:`nums[1:]`.
    """
    x, *ns = (num.value for num in nums)
    y: Union[float, Fraction] = 0
    for n in ns:
        y += n
    return am.Numeric(x - y)


@_make_function("*")
def _mul(_env: ev.Environment, *nums: am.Numeric) -> am.Numeric:
    """Returns the product of :data:`nums`."""
    prod: Union[float, Fraction] = 1
    for num in nums:
        prod *= num.value
    return am.Numeric(prod)


@_make_function("/")
def _div(_env: ev.Environment, *nums: am.Numeric) -> am.Numeric:
    """
    Divides :data:`nums[0]` and the product of :data:`nums[1:]`
    """
    x, *ns = (num.value for num in nums)
    y: Union[float, Fraction] = 1
    for n in ns:
        y *= n
    return am.Numeric(x / y)


@_make_function("setn", defer=True)
def _setn(
    env: ev.Environment,
    name: am.Quoted[am.Symbol],
    amalgam: am.Quoted[am.Amalgam],
) -> am.Amalgam:
    """
    Binds :data:`name` to the evaluated :data:`amalgam` value in the
    immediate :data:`env` and returns that value.
    """
    env[name.value.value] = amalgam.value.evaluate(env)
    return env[name.value.value]


@_make_function("fn", defer=True)
def _fn(
    env: ev.Environment,
    args: am.Quoted[am.Vector[am.Symbol]],
    body: am.Quoted[am.Amalgam],
) -> am.Function:
    """
    Creates an anonymous function using the provided arguments.

    Binds :data:`env` to the created :class:`.amalgams.Function` if a
    closure is formed.
    """
    fn = am.create_fn("~lambda~", [arg.value for arg in args.value.vals], body.value)
    if env.parent is not None:
        fn.bind(env)
    return fn


@_make_function("mkfn", defer=True)
def _mkfn(
    env: ev.Environment,
    name: am.Quoted[am.Symbol],
    args: am.Quoted[am.Vector[am.Symbol]],
    body: am.Quoted[am.Amalgam],
) -> am.Amalgam:
    """
    Creates a named function using the provided arguments.

    Composes :func:`._fn` and :func:`._setn`.
    """
    return _setn(env, name, am.Quoted(_fn(env, args, body).with_name(name.value.value)))


@_make_function("let", defer=True)
def _let(
    env: ev.Environment,
    qpairs: am.Quoted[am.Vector[am.Vector]],
    body: am.Quoted[am.Amalgam],
) -> am.Amalgam:
    """
    Creates temporary bindings of names to values specified in
    :data:`qpairs` before evaluating :data:`body`.
    """
    names = []
    values = []

    for pos, pair in enumerate(qpairs.value.vals):
        if not isinstance(pair, am.Vector) or len(pair.vals) != 2:
            raise ValueError(f"{pair} at {pos} is not a pair")

        name, value = pair.vals

        if not isinstance(name, am.Symbol):
            raise TypeError(f"{name} at {pos} is not a symbol")

        names.append(name)
        values.append(value)

    return _fn(env, am.Quoted(am.Vector(*names)), body).call(env, *values)


@_make_function("bool")
def _bool(_env: ev.Environment, expr: am.Amalgam) -> am.Atom:
    """Checks for the truthiness of an :data:`expr`."""
    if expr == am.String(""):
        return am.Atom("FALSE")
    elif expr == am.Numeric(0):
        return am.Atom("FALSE")
    elif expr == am.Vector():
        return am.Atom("FALSE")
    elif expr == am.Atom("FALSE"):
        return am.Atom("FALSE")
    elif expr == am.Atom("NIL"):
        return am.Atom("FALSE")
    return am.Atom("TRUE")


@_make_function(">")
def _gt(_env: ev.Environment, x: am.Amalgam, y: am.Amalgam) -> am.Atom:
    """Performs a `greater than` comparison."""
    if x > y:  # type: ignore
        return am.Atom("TRUE")
    return am.Atom("FALSE")


@_make_function("<")
def _lt(_env: ev.Environment, x: am.Amalgam, y: am.Amalgam) -> am.Atom:
    """Performs a `less than` comparison."""
    if x < y:  # type: ignore
        return am.Atom("TRUE")
    return am.Atom("FALSE")


@_make_function("=")
def _eq(_env: ev.Environment, x: am.Amalgam, y: am.Amalgam) -> am.Atom:
    """Performs an `equals` comparison."""
    if x == y:
        return am.Atom("TRUE")
    return am.Atom("FALSE")


@_make_function("/=")
def _ne(_env: ev.Environment, x: am.Amalgam, y: am.Amalgam) -> am.Atom:
    """Performs a `not equals` comparison."""
    if x != y:
        return am.Atom("TRUE")
    return am.Atom("FALSE")


@_make_function(">=")
def _ge(env: ev.Environment, x: am.Amalgam, y: am.Amalgam) -> am.Atom:
    """Performs a `greater than or equal` comparison."""
    if x >= y:  # type: ignore
        return am.Atom("TRUE")
    return am.Atom("FALSE")


@_make_function("<=")
def _le(env: ev.Environment, x: am.Amalgam, y: am.Amalgam) -> am.Atom:
    """Performs a `less than or equal` comparison."""
    if x <= y:  # type: ignore
        return am.Atom("TRUE")
    return am.Atom("FALSE")


@_make_function("not")
def _not(_env: ev.Environment, expr: am.Amalgam) -> am.Atom:
    """Checks and negates the truthiness of :data:`expr`."""
    if _bool(_env, expr) == am.Atom("TRUE"):
        return am.Atom("FALSE")
    return am.Atom("TRUE")


@_make_function("and", defer=True)
def _and(env: ev.Environment, *qexprs: am.Quoted[am.Amalgam]) -> am.Atom:
    """
    Checks the truthiness of the evaluated :data:`qexprs` and performs
    an `and` operation. Short-circuits when :data:`:FALSE` is returned
    and does not evaluate subsequent expressions.
    """
    for qexpr in qexprs:
        cond = _bool(env, qexpr.value.evaluate(env))
        if cond == am.Atom("FALSE"):
            return cond
    return am.Atom("TRUE")


@_make_function("or", defer=True)
def _or(env: ev.Environment, *qexprs: am.Quoted[am.Amalgam]) -> am.Atom:
    """
    Checks the truthiness of the evaluated :data:`qexprs` and performs
    an `or` operation. Short-circuits when :data:`:TRUE` is returned
    and does not evaluate subsequent expressions.
    """
    for qexpr in qexprs:
        cond = _bool(env, qexpr.value.evaluate(env))
        if cond == am.Atom("TRUE"):
            return cond
    return am.Atom("FALSE")


@_make_function("if", defer=True)
def _if(
    env: ev.Environment,
    qcond: am.Quoted[am.Amalgam],
    qthen: am.Quoted[am.Amalgam],
    qelse: am.Quoted[am.Amalgam],
) -> am.Amalgam:
    """
    Checks the truthiness of the evaluated :data:`qcond`, evaluates and
    returns :data:`qthen` if :data:`:TRUE`, otherwise, evaluates and
    returns :data:`qelse`.
    """
    cond = _bool(env, qcond.value.evaluate(env))
    if cond == am.Atom("TRUE"):
        return qthen.value.evaluate(env)
    return qelse.value.evaluate(env)


@_make_function("cond", defer=True)
def _cond(env: ev.Environment, *qpairs: am.Quoted[am.Vector[am.Amalgam]]) -> am.Amalgam:
    """
    Traverses pairs of conditions and values. If the condition evaluates
    to :data:`:TRUE`, returns the value pair and short-circuits
    evaluation. If no conditions are met, :data:`:NIL` is returned.
    """
    for qpair in qpairs:
        pred, expr = qpair.value.vals
        if _bool(env, pred.evaluate(env)) == am.Atom("TRUE"):
            return expr.evaluate(env)
    return am.Atom("NIL")


@_make_function("exit")
def _exit(env: ev.Environment, exit_code: am.Numeric = am.Numeric(0)) -> am.Amalgam:
    """Exits the program with the given :data:`exit_code`."""
    print("Goodbye.")
    sys.exit(int(exit_code.value))


@_make_function("print")
def _print(_env: ev.Environment, amalgam: am.Amalgam) -> am.Amalgam:
    """Prints the provided :data:`amalgam` and returns it."""
    print(amalgam)
    return amalgam


@_make_function("putstrln")
def _putstrln(_env: ev.Environment, string: am.String) -> am.String:
    """Prints the provided :data:`string` and returns it."""
    if not isinstance(string, am.String):
        raise TypeError("putstrln only accepts a string")
    print(string.value)
    return string


@_make_function("do", defer=True)
def _do(env: ev.Environment, *qexprs: am.Quoted[am.Amalgam]) -> am.Amalgam:
    """
    Evaluates a variadic amount of :data:`qexprs`, returning the final
    expression evaluated.
    """
    accumulator = am.Atom("NIL")
    for qexpr in qexprs:
        accumulator = qexpr.value.evaluate(env)
    return accumulator


@_make_function("require")
def _require(env: ev.Environment, module_name: am.String) -> am.Atom:
    """
    Runs a given :data:`module_name` and imports the exposed symbols to
    the current :data:`env` with respect to the `~provides~` key created
    in :func:`._provide`.
    """
    module_path = Path(module_name.value).absolute()
    with module_path.open("r", encoding="UTF-8") as f:
        text = f.read()

    snapshot = env.bindings.copy()

    internal_engine = cast(am.Internal[en.Engine], env["~engine~"])
    internal_engine.value.parse_and_run(text)

    if "~provides~" in env:
        symbols = cast(am.Vector[am.Symbol], env["~provides~"])
        exports = {symbol.value for symbol in symbols.vals}

        changes = {
            name: env[name]
            for name in exports.intersection(env.bindings)
        }

        snapshot.update(changes)
        env.bindings = snapshot

    return am.Atom("NIL")


@_make_function("provide", defer=True)
def _provide(env: ev.Environment, *qsymbols: am.Quoted[am.Symbol]) -> am.Atom:
    """Sets the `~provides~` key to be used in :func:`._require`."""
    env["~provides~"] = am.Vector(*(qsymbol.value for qsymbol in qsymbols))
    return am.Atom("NIL")


@_make_function("concat")
def _concat(_env: ev.Environment, *strings: am.String) -> am.String:
    """Concatenates the given :data:`strings`."""
    return am.String("".join(string.value for string in strings))


@_make_function("merge")
def _merge(_env: ev.Environment, *vectors: am.Vector) -> am.Vector:
    """Merges the given :data:`vectors`."""
    return am.Vector(*chain.from_iterable(vector.vals for vector in vectors))


@_make_function("slice")
def _slice(
    _env: ev.Environment,
    vector: am.Vector,
    start: am.Numeric,
    stop: am.Numeric,
    step: am.Numeric = am.Numeric(1),
) -> am.Vector:
    """Returns a slice of the given :data:`vector`."""
    return am.Vector(*vector.vals[start.value:stop.value:step.value])


@_make_function("at")
def _at(_env: ev.Environment, index: am.Numeric, vector: am.Vector) -> am.Amalgam:
    """Indexes :data:`vector` with :data:`index`."""
    return vector.vals[index.value]


@_make_function("remove")
def _remove(_env: ev.Environment, index: am.Numeric, vector: am.Vector) -> am.Vector:
    """Removes an item in :data:`vector` using :data:`index`."""
    vals = list(vector.vals)
    del vals[index.value]
    return am.Vector(*vals)


@_make_function("len")
def _len(_env: ev.Environment, vector: am.Vector) -> am.Numeric:
    """Returns the length of a :data:`vector`."""
    return am.Numeric(len(vector.vals))


@_make_function("cons")
def _cons(_env: ev.Environment, amalgam: am.Amalgam, vector: am.Vector) -> am.Vector:
    """Preprends an :data:`amalgam` to :data:`vector`."""
    return am.Vector(amalgam, *vector.vals)


@_make_function("snoc")
def _snoc(_env: ev.Environment, vector: am.Vector, amalgam: am.Amalgam) -> am.Vector:
    """Appends an :data:`amalgam` to :data:`vector`."""
    return am.Vector(*vector.vals, amalgam)


@_make_function("is-map")
def _is_map(_env: ev.Environment, vector: am.Vector) -> am.Atom:
    """Verifies whether :data:`vector` is a mapping."""
    if vector.mapping:
        return am.Atom("TRUE")
    return am.Atom("FALSE")


@_make_function("map-in")
def _map_in(_env: ev.Environment, vector: am.Vector, atom: am.Atom) -> am.Atom:
    """Checks whether :data:`atom` is a member of :data:`vector`."""
    if not vector.mapping:
        raise ValueError("the given vector is not a mapping")
    if atom.value in vector.mapping:
        return am.Atom("TRUE")
    return am.Atom("FALSE")


@_make_function("map-at")
def _map_at(_env: ev.Environment, vector: am.Vector, atom: am.Atom) -> am.Amalgam:
    """Obtains the value bound to :data:`atom` in :data:`vector`."""
    if not vector.mapping:
        raise ValueError("the given vector is not a mapping")
    return vector.mapping[atom.value]


@_make_function("map-up")
def _map_up(
    _env: ev.Environment,
    vector: am.Vector,
    atom: am.Atom,
    amalgam: am.Amalgam,
) -> am.Vector:
    """
    Updates the :data:`vector mapping with :data:`atom`, and
    :data:`amalgam`.
    """
    if not vector.mapping:
        raise ValueError("the given vector is not a mapping")

    new_vector: am.Vector[am.Amalgam] = am.Vector()

    mapping = {**vector.mapping}
    mapping[atom.value] = amalgam

    vals: List[am.Amalgam] = []
    for name, value in mapping.items():
        vals += (am.Atom(name), value)

    new_vector.vals = tuple(vals)
    new_vector.mapping = mapping

    return new_vector


class _Return(NamedTuple):
    """Internal utility class for signalling a return value."""
    return_value: am.Amalgam


@_make_function("return", contextual=True)
def _return(env: ev.Environment, result: am.Amalgam) -> am.Internal:
    """Exits a context with a :data:`result`."""
    return am.Internal(_Return(result))


@_make_function("break", contextual=True)
def _break(env: ev.Environment) -> am.Internal:
    """Exits a loop with :data:`:NIL`."""
    return am.Internal(_Return(am.Atom("NIL")))


@_make_function("loop", defer=True, allows=("break", "return"))
def _loop(env: ev.Environment, *qexprs: am.Quoted[am.Amalgam]) -> am.Amalgam:
    """
    Loops through and evaluates :data:`qexprs` indefinitely until a
    :data:`break` or :data:`return` is encountered.
    """
    return_value = None

    while return_value is None:
        for qexpr in qexprs:
            result = qexpr.value.evaluate(env)
            if isinstance(result, am.Internal):
                if isinstance(result.value, _Return):  # pragma: no branch
                    return_value = result.value.return_value
                break

    return return_value


@_make_function("when", defer=True)
def _when(
    env: ev.Environment, qcond: am.Quoted[am.Amalgam], qbody: am.Quoted[am.Amalgam],
) -> am.Amalgam:
    """
    Synonym for :func:`._if` that defaults :data:`qelse` to
    :data:`:NIL`.
    """
    cond = _bool(env, qcond.value.evaluate(env))
    if cond == am.Atom("TRUE"):
        return qbody.value.evaluate(env)
    return am.Atom("NIL")


@_make_function("eval")
def _eval(env: ev.Environment, amalgam: am.Amalgam) -> am.Amalgam:
    """Evaluates a given :data:`amalgam`."""
    if isinstance(amalgam, am.Quoted):
        amalgam = amalgam.value
    return amalgam.evaluate(env)


@_make_function("unquote")
def _unquote(_env: ev.Environment, qamalgam: am.Quoted[am.Amalgam]) -> am.Amalgam:
    """Unquotes a given :data:`qamalgam`."""
    if not isinstance(qamalgam, am.Quoted):
        raise TypeError("unquotable value provided")
    return qamalgam.value


@_make_function("setr", defer=True)
def _setr(
    env: ev.Environment,
    qrname: am.Quoted[am.Symbol],
    qamalgam: am.Quoted[am.Amalgam],
) -> am.Amalgam:
    """
    Attemps to resolve :data:`qrname` to a :class:`.amalgams.Symbol`
    and binds it to the evaluated :data:`qamalgam` in the immediate
    :data:`env`.
    """
    rname = qrname.value.evaluate(env)

    if not isinstance(rname, am.Symbol):
        raise TypeError("could not resolve to a symbol")

    amalgam = qamalgam.value.evaluate(env)
    env[rname.value] = amalgam

    return amalgam


@_make_function("macro", defer=True)
def _macro(
    env: ev.Environment,
    name: am.Quoted[am.Symbol],
    args: am.Quoted[am.Vector[am.Symbol]],
    body: am.Quoted[am.Amalgam],
) -> am.Amalgam:
    """Creates a named macro using the provided arguments."""
    fn = am.create_fn(
        name.value.value,
        [arg.value for arg in args.value.vals],
        body.value,
        defer=True,
    )

    if env.parent is not None:
        fn.bind(env)

    return _setn(env, name, am.Quoted(fn))
