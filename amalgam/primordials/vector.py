from __future__ import annotations

from itertools import chain
from typing import List, TYPE_CHECKING

import amalgam.amalgams as am
from amalgam.primordials.utils import make_function


if TYPE_CHECKING:  # pragma: no cover
    from amalgam.environment import Environment
    from amalgam.primordials.utils import Store


VECTOR: Store = {}


@make_function(VECTOR, "merge")
def _merge(env: Environment, *vectors: am.Vector) -> am.Vector:
    """Merges the given :data:`vectors`."""
    return am.Vector(*chain.from_iterable(vectors))


@make_function(VECTOR, "slice")
def _slice(
    env: Environment,
    vector: am.Vector,
    start: am.Numeric,
    stop: am.Numeric,
    step: am.Numeric = am.Numeric(1),
) -> am.Vector:
    """Returns a slice of the given :data:`vector`."""
    return am.Vector(*vector.vals[start.value:stop.value:step.value])


@make_function(VECTOR, "at")
def _at(env: Environment, index: am.Numeric, vector: am.Vector) -> am.Amalgam:
    """Indexes :data:`vector` with :data:`index`."""
    return vector.vals[index.value]


@make_function(VECTOR, "remove")
def _remove(env: Environment, index: am.Numeric, vector: am.Vector) -> am.Vector:
    """Removes an item in :data:`vector` using :data:`index`."""
    vals = list(vector)
    del vals[index.value]
    return am.Vector(*vals)


@make_function(VECTOR, "len")
def _len(env: Environment, vector: am.Vector) -> am.Numeric:
    """Returns the length of a :data:`vector`."""
    return am.Numeric(len(vector))


@make_function(VECTOR, "cons")
def _cons(env: Environment, amalgam: am.Amalgam, vector: am.Vector) -> am.Vector:
    """Preprends an :data:`amalgam` to :data:`vector`."""
    return am.Vector(amalgam, *vector)


@make_function(VECTOR, "snoc")
def _snoc(env: Environment, vector: am.Vector, amalgam: am.Amalgam) -> am.Vector:
    """Appends an :data:`amalgam` to :data:`vector`."""
    return am.Vector(*vector, amalgam)


@make_function(VECTOR, "is-map")
def _is_map(env: Environment, vector: am.Vector) -> am.Atom:
    """Verifies whether :data:`vector` is a mapping."""
    if vector.mapping:
        return am.Atom("TRUE")
    return am.Atom("FALSE")


@make_function(VECTOR, "map-in")
def _map_in(env: Environment, vector: am.Vector, atom: am.Atom) -> am.Atom:
    """Checks whether :data:`atom` is a member of :data:`vector`."""
    if not vector.mapping:
        raise ValueError("the given vector is not a mapping")
    if atom.value in vector.mapping:
        return am.Atom("TRUE")
    return am.Atom("FALSE")


@make_function(VECTOR, "map-at")
def _map_at(env: Environment, vector: am.Vector, atom: am.Atom) -> am.Amalgam:
    """Obtains the value bound to :data:`atom` in :data:`vector`."""
    if not vector.mapping:
        raise ValueError("the given vector is not a mapping")
    return vector.mapping[atom.value]


@make_function(VECTOR, "map-up")
def _map_up(
    env: Environment,
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
