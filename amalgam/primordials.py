from functools import partial
from typing import Callable, Dict, TypeVar, Union

from amalgam.amalgams import (
    Amalgam,
    Function,
)


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
