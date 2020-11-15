from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import amalgam.amalgams as am
from amalgam.primordials.utils import make_function


if TYPE_CHECKING:  # pragma: no cover
    from amalgam.environment import Environment
    from amalgam.primordials.utils import Store


IO_Store: Store = {}


@make_function(IO_Store, "print")
def _print(env: Environment, amalgam: am.Amalgam) -> am.Amalgam:
    """Prints the provided :data:`amalgam` and returns it."""
    print(amalgam)
    return amalgam


@make_function(IO_Store, "putstrln")
def _putstrln(env: Environment, string: am.String) -> am.String:
    """Prints the provided :data:`string` and returns it."""
    if not isinstance(string, am.String):
        raise TypeError("putstrln only accepts a string")
    print(string.value)
    return string


@make_function(IO_Store, "exit")
def _exit(env: Environment, exit_code: am.Numeric = am.Numeric(0)) -> am.Amalgam:
    """Exits the program with the given :data:`exit_code`."""
    print("Goodbye.")
    sys.exit(int(exit_code.value))
