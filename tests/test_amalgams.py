import re
from typing import Any

from amalgam.amalgams import (
    Amalgam,
    Environment,
    Numeric,
)

from hypothesis import given
from hypothesis.strategies import (
    integers, floats, fractions,
    lists, one_of,
)


_non_scientific_float = floats(
    allow_infinity=False,
    allow_nan=False,
).map(str).filter(lambda f: not re.search("[Ee][+-][0-9]+", f)).map(float)

_numeric = one_of(integers(), _non_scientific_float, fractions()).map(Numeric)


def _common_repr(inst: Amalgam):
    return fr"<{inst.__class__.__name__} '.+' @ {hex(id(inst))}>"


@given(_numeric)
def test_numeric_evaluate(numeric):
    assert numeric == numeric.evaluate(Environment())


@given(_numeric)
def test_numeric_repr(numeric):
    assert re.match(_common_repr(numeric), repr(numeric))
