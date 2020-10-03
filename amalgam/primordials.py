from fractions import Fraction
from functools import partial
from typing import Callable, Dict, TypeVar, Union

from amalgam.amalgams import (
    Amalgam,
    Environment,
    Function,
    Numeric,
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