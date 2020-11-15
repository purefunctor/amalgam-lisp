from __future__ import annotations

from fractions import Fraction
from typing import Union, TYPE_CHECKING

import amalgam.amalgams as am
from amalgam.primordials.utils import make_function


if TYPE_CHECKING:  # pragma: no cover
    from amalgam.environment import Environment
    from amalgam.primordials.utils import Store


ARITHMETIC: Store = {}


@make_function(ARITHMETIC, "+")
def _add(env: Environment, *nums: am.Numeric) -> am.Numeric:
    """Returns the sum of :data:`nums`."""
    return am.Numeric(sum(num.value for num in nums))


@make_function(ARITHMETIC, "-")
def _sub(env: Environment, *nums: am.Numeric) -> am.Numeric:
    """
    Subtracts :data:`nums[0]` and the summation of :data:`nums[1:]`.
    """
    x, *ns = (num.value for num in nums)
    y: Union[float, Fraction] = 0
    for n in ns:
        y += n
    return am.Numeric(x - y)


@make_function(ARITHMETIC, "*")
def _mul(env: Environment, *nums: am.Numeric) -> am.Numeric:
    """Returns the product of :data:`nums`."""
    prod: Union[float, Fraction] = 1
    for num in nums:
        prod *= num.value
    return am.Numeric(prod)


@make_function(ARITHMETIC, "/")
def _div(env: Environment, *nums: am.Numeric) -> am.Numeric:
    """
    Divides :data:`nums[0]` and the product of :data:`nums[1:]`
    """
    x, *ns = (num.value for num in nums)
    y: Union[float, Fraction] = 1
    for n in ns:
        y *= n
    return am.Numeric(x / y)
