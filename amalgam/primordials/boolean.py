from __future__ import annotations

from typing import TYPE_CHECKING

import amalgam.amalgams as am
from amalgam.primordials.utils import make_function


if TYPE_CHECKING:  # pragma: no cover
    from amalgam.environment import Environment
    from amalgam.primordials.utils import Store


BOOLEAN: Store = {}


@make_function(BOOLEAN, "bool")
def _bool(env: Environment, expr: am.Amalgam) -> am.Atom:
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


@make_function(BOOLEAN, "not")
def _not(env: Environment, expr: am.Amalgam) -> am.Atom:
    """Checks and negates the truthiness of :data:`expr`."""
    if _bool(env, expr) == am.Atom("TRUE"):
        return am.Atom("FALSE")
    return am.Atom("TRUE")


@make_function(BOOLEAN, "and", defer=True)
def _and(env: Environment, *exprs: am.Amalgam) -> am.Atom:
    """
    Checks the truthiness of the evaluated :data:`exprs` and performs
    an `and` operation. Short-circuits when :data:`:FALSE` is returned
    and does not evaluate subsequent expressions.
    """
    for expr in exprs:
        cond = _bool(env, expr.evaluate(env))
        if cond == am.Atom("FALSE"):
            return cond
    return am.Atom("TRUE")


@make_function(BOOLEAN, "or", defer=True)
def _or(env: Environment, *exprs: am.Amalgam) -> am.Atom:
    """
    Checks the truthiness of the evaluated :data:`exprs` and performs
    an `or` operation. Short-circuits when :data:`:TRUE` is returned
    and does not evaluate subsequent expressions.
    """
    for expr in exprs:
        cond = _bool(env, expr.evaluate(env))
        if cond == am.Atom("TRUE"):
            return cond
    return am.Atom("FALSE")
