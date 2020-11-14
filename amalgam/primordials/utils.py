from __future__ import annotations

from functools import partial, wraps
from typing import (
    cast,
    overload,
    Callable,
    List,
    MutableMapping,
    Sequence,
    TypeVar,
    Union,
    TYPE_CHECKING,
)

import amalgam.amalgams as am


if TYPE_CHECKING:  # pragma: no cover
    from amalgam.environment import Environment

    Store = MutableMapping[str, am.Function]


T = TypeVar("T", bound=am.Amalgam)


@overload
def make_function(
    store: Store,
    name: str,
    func: Callable[..., T],
    defer: bool = False,
    contextual: bool = False,
    allows: Sequence[str] = None,
) -> Callable[..., T]:  # pragma: no cover
    ...


@overload
def make_function(
    store: Store,
    name: str,
    func: None = None,
    defer: bool = False,
    contextual: bool = False,
    allows: Sequence[str] = None,
) -> partial:  # pragma: no cover
    ...


def make_function(
    store, name, func=None, defer=False, contextual=False, allows=None,
) -> Union[partial, Callable[..., T]]:
    """
    Transforms a :data:`func` into a :class:`.amalgams.Function` and
    places it inside of a :data:`store`.
    """

    if func is None:
        return partial(
            make_function,
            store,
            name,
            defer=defer,
            contextual=contextual,
            allows=allows,
        )

    if allows is None:
        allows = []

    @wraps(func)
    def _func(
        env: Environment, *arguments: am.Amalgam, **keywords: am.Amalgam
    ) -> am.Amalgam:
        with env.search_at(depth=-1):
            fns = cast(List[am.Function], [env[allow] for allow in allows])

        for fn in fns:
            fn.in_context = True

        result = func(env, *arguments, **keywords)

        for fn in fns:
            fn.in_context = False

        return result

    store[name] = am.Function(name, _func, defer, contextual)

    return _func
