from __future__ import annotations

from typing import TYPE_CHECKING

import amalgam.amalgams as am
import amalgam.primordials.boolean as boolean
from amalgam.primordials.utils import make_function


if TYPE_CHECKING:  # pragma: no cover
    from amalgam.environment import Environment
    from amalgam.primordials.utils import Store


CONTROL: Store = {}


@make_function(CONTROL, "if", defer=True)
def _if(
    env: Environment, cond: am.Amalgam, then: am.Amalgam, else_: am.Amalgam,
) -> am.Amalgam:
    """
    Checks the truthiness of the evaluated :data:`cond`, evaluates and
    returns :data:`then` if :data:`:TRUE`, otherwise, evaluates and
    returns :data:`else_`.
    """
    cond = boolean._bool(env, cond.evaluate(env))
    if cond == am.Atom("TRUE"):
        return then.evaluate(env)
    return else_.evaluate(env)


@make_function(CONTROL, "when", defer=True)
def _when(
    env: Environment, cond: am.Amalgam, body: am.Amalgam,
) -> am.Amalgam:
    """
    Synonym for :func:`._if` that defaults :data:`else` to
    :data:`:NIL`.
    """
    cond = boolean._bool(env, cond.evaluate(env))
    if cond == am.Atom("TRUE"):
        return body.evaluate(env)
    return am.Atom("NIL")


@make_function(CONTROL, "cond", defer=True)
def _cond(env: Environment, *pairs: am.Vector[am.Amalgam]) -> am.Amalgam:
    """
    Traverses pairs of conditions and values. If the condition evaluates
    to :data:`:TRUE`, returns the value pair and short-circuits
    evaluation. If no conditions are met, :data:`:NIL` is returned.
    """
    for pair in pairs:
        pred, expr = pair
        if boolean._bool(env, pred.evaluate(env)) == am.Atom("TRUE"):
            return expr.evaluate(env)
    return am.Atom("NIL")


@make_function(CONTROL, "do", defer=True)
def _do(env: Environment, *exprs: am.Amalgam) -> am.Amalgam:
    """
    Evaluates a variadic amount of :data:`exprs`, returning the final
    expression evaluated.
    """
    accumulator: am.Amalgam = am.Atom("NIL")
    for expr in exprs:
        accumulator = expr.evaluate(env)
    return accumulator


@make_function(CONTROL, "return", contextual=True)
def _return(env: Environment, result: am.Amalgam) -> am.Vector:
    """Exits a context with a :data:`result`."""
    return am.Vector(am.Atom("payload"), result)


@make_function(CONTROL, "break", contextual=True)
def _break(env: Environment) -> am.Vector:
    """Exits a loop with :data:`:NIL`."""
    return am.Vector(am.Atom("payload"), am.Atom("NIL"))


@make_function(CONTROL, "loop", defer=True, allows=("break", "return"))
def _loop(env: Environment, *exprs: am.Amalgam) -> am.Amalgam:
    """
    Loops through and evaluates :data:`exprs` indefinitely until a
    :data:`break` or :data:`return` is encountered.
    """
    while True:
        for expr in exprs:
            result = expr.evaluate(env)
            try:
                return result.mapping["payload"]
            except (AttributeError, KeyError):
                pass
