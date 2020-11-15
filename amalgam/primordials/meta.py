from __future__ import annotations

from typing import TYPE_CHECKING

import amalgam.amalgams as am
from amalgam.primordials.utils import make_function


if TYPE_CHECKING:  # pragma: no cover
    from amalgam.environment import Environment
    from amalgam.primordials.utils import Store


META: Store = {}


@make_function(META, "setn", defer=True)
def _setn(env: Environment, name: am.Symbol, amalgam: am.Amalgam) -> am.Amalgam:
    """
    Binds :data:`name` to the evaluated :data:`amalgam` value in the
    immediate :data:`env` and returns that value.
    """
    value = amalgam.evaluate(env)
    if isinstance(value, am.Notification):
        value.push(am.Atom("setn"), env, "inherited")
        return value
    else:
        env[name.value] = value
        return env[name.value]


@make_function(META, "setr", defer=True)
def _setr(
    env: Environment, rname: am.Amalgam, amalgam: am.Amalgam,
) -> am.Amalgam:
    """
    Attemps to resolve :data:`rname` to a :class:`.amalgams.Symbol`
    and binds it to the evaluated :data:`amalgam` in the immediate
    :data:`env`.
    """
    rname = rname.evaluate(env)

    if not isinstance(rname, am.Symbol):
        raise TypeError("could not resolve to a symbol")

    amalgam = amalgam.evaluate(env)
    env[rname.value] = amalgam

    return amalgam


@make_function(META, "unquote")
def _unquote(env: Environment, qamalgam: am.Quoted[am.Amalgam]) -> am.Amalgam:
    """Unquotes a given :data:`qamalgam`."""
    if not isinstance(qamalgam, am.Quoted):
        raise TypeError("unquotable value provided")
    return qamalgam.value


@make_function(META, "eval")
def _eval(env: Environment, amalgam: am.Amalgam) -> am.Amalgam:
    """Evaluates a given :data:`amalgam`."""
    if isinstance(amalgam, am.Quoted):
        amalgam = amalgam.value
    return amalgam.evaluate(env)


@make_function(META, "fn", defer=True)
def _fn(
    env: Environment, args: am.Vector[am.Symbol], body: am.Amalgam,
) -> am.Function:
    """
    Creates an anonymous function using the provided arguments.

    Binds :data:`env` to the created :class:`.amalgams.Function` if a
    closure is formed.
    """
    fn = am.create_fn("~lambda~", [arg.value for arg in args], body)
    if env.parent is not None:
        fn.bind(env)
    return fn


@make_function(META, "mkfn", defer=True)
def _mkfn(
    env: Environment, name: am.Symbol, args: am.Vector[am.Symbol], body: am.Amalgam,
) -> am.Amalgam:
    """
    Creates a named function using the provided arguments.

    Composes :func:`._fn` and :func:`._setn`.
    """
    return _setn(env, name, _fn(env, args, body).with_name(name.value))


@make_function(META, "macro", defer=True)
def _macro(
    env: Environment,
    name: am.Symbol,
    args: am.Vector[am.Symbol],
    body: am.Amalgam,
) -> am.Amalgam:
    """Creates a named macro using the provided arguments."""
    fn = am.create_fn(
        name.value,
        [arg.value for arg in args],
        body,
        defer=True,
    )

    if env.parent is not None:
        fn.bind(env)

    return _setn(env, name, fn)


@make_function(META, "let", defer=True)
def _let(
    env: Environment, pairs: am.Vector[am.Vector], body: am.Amalgam,
) -> am.Amalgam:
    """
    Creates temporary bindings of names to values specified in
    :data:`pairs` before evaluating :data:`body`.
    """
    names = []
    values = []

    for pair in pairs:
        if not isinstance(pair, am.Vector) or len(pair) != 2:
            notification = am.Notification()
            notification.push(pair, env, "not a pair")
            return notification

        name, value = pair

        if not isinstance(name, am.Symbol):
            notification = am.Notification()
            notification.push(name, env, "not a symbol")
            return notification

        names.append(name)
        values.append(value)

    return _fn(env, am.Vector(*names), body).call(env, *values)
