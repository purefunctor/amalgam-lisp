from __future__ import annotations

from abc import ABC, abstractmethod
from fractions import Fraction
from itertools import chain
from typing import (
    Any,
    Dict,
    Iterator,
    MutableMapping,
    Optional,
    Union,
)


class Amalgam(ABC):
    """The abstract base class for language constructs."""

    def bind(self, environment: Environment) -> Amalgam:
        """
        Protocol for binding environments to `Amalgam` objects.

        This is responsible for binding `environment`s to `Amalgam`
        objects that utilize closures such as curried functions.
        """

    @abstractmethod
    def evaluate(self, environment: Environment, *arguments: Any) -> Any:
        """
        Protocol for evaluating or unwrapping `Amalgam` objects.

        This is responsible for evaluating or reducing `Amalgam`
        objects given a specific `environment`.
        """

    def _make_repr(self, value: Any) -> str:
        """Helper method for creating `__repr__` for subclasses."""
        return f"<{self.__class__.__name__} '{value!s}' @ {hex(id(self))}>"


class Numeric(Amalgam):
    """An `Amalgam` that wraps around numeric types."""

    def __init__(self, value: Union[int, float, Fraction]) -> None:
        self.value = value

    def evaluate(self, _environment: Environment, *_arguments: Any) -> Numeric:
        return self

    def __repr__(self) -> str:
        return self._make_repr(self.value)


class String(Amalgam):
    """An `Amalgam` that wraps around strings."""

    def __init__(self, value: str) -> None:
        self.value = value

    def evaluate(self, _environment: Environment, *_arguments: Any) -> String:
        return self

    def __repr__(self) -> str:
        return self._make_repr(f"\"{self.value}\"")


Bindings = Dict[str, Amalgam]


class Environment(MutableMapping[str, Amalgam]):
    """Class that represents nested execution environments."""

    def __init__(
        self,
        parent: Optional[Environment] = None,
        bindings: Optional[Bindings] = None,
    ) -> None:

        self.parent: Optional[Environment] = parent

        self.level: int = parent.level + 1 if parent else 0

        self.bindings: Bindings = bindings if bindings else {}

    def __getitem__(self, item: str) -> Amalgam:
        """Performs `__getitem__` on nested environments."""
        if self.ihas(item) or self.parent is None:
            return self.iget(item)

        else:
            return self.parent[item]

    def __setitem__(self, item: str, value: Amalgam) -> None:
        """Performs `__setitem__` on nested environments."""
        if self.ihas(item) or self.parent is None:
            self.iset(item, value)

        else:
            self.parent[item] = value

    def __delitem__(self, item: str) -> None:
        """Performs `__deltitem__` on nested environments."""
        if self.ihas(item) or self.parent is None:
            self.idel(item)

        else:
            del self.parent[item]

    def __contains__(self, item: object) -> bool:
        """Performs `__contains__` on nested environments."""
        if self.ihas(item) or self.parent is None:
            return self.ihas(item)

        else:
            return item in self.parent

    def __iter__(self) -> Iterator[str]:
        """Performs `__iter__` on nested environments."""
        if self.parent is None:
            return self.iiter()

        else:
            return chain(self.parent, self.iiter())

    def __len__(self) -> int:
        """Performs `__len__` on nested environments."""
        if self.parent is None:
            return self.ilen()

        else:
            return len(self.parent) + self.ilen()

    def iget(self, item: str) -> Amalgam:
        """Performs `__getitem__` on the immediate environment."""
        return self.bindings[item]

    def iset(self, item: str, value: Amalgam) -> None:
        """Performs `__setitem__` on the immediate environment."""
        self.bindings[item] = value

    def idel(self, item: str) -> None:
        """Performs `__delitem__` on the immediate environment."""
        del self.bindings[item]

    def ihas(self, item: object) -> bool:
        """Performs `__contains__` on the immediate environment."""
        return item in self.bindings

    def iiter(self) -> Iterator[str]:
        """Performs `__iter__` on the immediate environment."""
        return iter(self.bindings)

    def ilen(self) -> int:
        """Performs `__len__` on the immediate environment."""
        return len(self.bindings)

    def env_push(self, bindings: Optional[Bindings] = None) -> Environment:
        """Creates a new child environment."""
        return Environment(self, bindings)

    def env_pop(self) -> Environment:
        """Discards the current environment."""
        if self.parent is not None:
            return self.parent
        else:
            raise Exception("Cannot discard top-level `Environment`")
