from __future__ import annotations

from typing import TYPE_CHECKING

import amalgam.amalgams as am
from amalgam.primordials.utils import make_function


if TYPE_CHECKING:  # pragma: no cover
    from amalgam.environment import Environment
    from amalgam.primordials.utils import Store


STRING: Store = {}


@make_function(STRING, "concat")
def _concat(env: Environment, *strings: am.String) -> am.String:
    """Concatenates the given :data:`strings`."""
    return am.String("".join(string.value for string in strings))
