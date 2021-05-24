from __future__ import annotations

from functools import wraps
from mypy_extensions import Arg, KwArg, VarArg
from typing import (
    cast,
    Callable,
    List,
    MutableMapping,
    Sequence,
    TypeVar,
    TYPE_CHECKING,
)

import amalgam.amalgams as am


if TYPE_CHECKING:  # pragma: no cover
    from amalgam.environment import Environment

    Store = MutableMapping[str, am.Function]

    T = TypeVar("T", bound=am.Amalgam)

    _Function = Callable[
        [
            Arg(Environment, "env"),  # noqa: F821
            VarArg(am.Amalgam),
            KwArg(am.Amalgam),
        ],
        T
    ]


def make_function(
    store: Store,
    name: str,
    defer: bool = False,
    contextual: bool = False,
    allows: Sequence[str] = None,
) -> Callable[[Callable[..., T]], _Function[T]]:
    """
    Decorator factory for transforming some callable into a
    :class:`.amalgams.Function`, injecting it into a :data:`store`.
    """

    _allows = allows or []

    def _make_function(f: Callable[..., T]) -> _Function[T]:
        @wraps(f)
        def _f(
            env: Environment,
            *arguments: am.Amalgam,
            **keywords: am.Amalgam,
        ) -> T:

            with env.search_at(depth=-1):
                fns = cast(List[am.Function], [env[allow] for allow in _allows])

            for fn in fns:
                fn.in_context = True

            result = f(env, *arguments, **keywords)

            for fn in fns:
                fn.in_context = False

            return result

        store[name] = am.Function(name, _f, defer, contextual)

        return _f

    return _make_function
