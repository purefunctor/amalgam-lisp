from __future__ import annotations

from typing import TYPE_CHECKING

import amalgam.amalgams as am
from amalgam.primordials.utils import make_function


if TYPE_CHECKING:  # pragma: no cover
    from amalgam.environment import Environment
    from amalgam.primordials.utils import Store


COMPARISON: Store = {}


@make_function(COMPARISON, ">")
def _gt(env: Environment, x: am.Amalgam, y: am.Amalgam) -> am.Atom:
    """Performs a `greater than` comparison."""
    if x > y:  # type: ignore
        return am.Atom("TRUE")
    return am.Atom("FALSE")


@make_function(COMPARISON, "<")
def _lt(env: Environment, x: am.Amalgam, y: am.Amalgam) -> am.Atom:
    """Performs a `less than` comparison."""
    if x < y:  # type: ignore
        return am.Atom("TRUE")
    return am.Atom("FALSE")


@make_function(COMPARISON, "=")
def _eq(env: Environment, x: am.Amalgam, y: am.Amalgam) -> am.Atom:
    """Performs an `equals` comparison."""
    if x == y:
        return am.Atom("TRUE")
    return am.Atom("FALSE")


@make_function(COMPARISON, "/=")
def _ne(env: Environment, x: am.Amalgam, y: am.Amalgam) -> am.Atom:
    """Performs a `not equals` comparison."""
    if x != y:
        return am.Atom("TRUE")
    return am.Atom("FALSE")


@make_function(COMPARISON, ">=")
def _ge(env: Environment, x: am.Amalgam, y: am.Amalgam) -> am.Atom:
    """Performs a `greater than or equal` comparison."""
    if x >= y:  # type: ignore
        return am.Atom("TRUE")
    return am.Atom("FALSE")


@make_function(COMPARISON, "<=")
def _le(env: Environment, x: am.Amalgam, y: am.Amalgam) -> am.Atom:
    """Performs a `less than or equal` comparison."""
    if x <= y:  # type: ignore
        return am.Atom("TRUE")
    return am.Atom("FALSE")
