from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    Any,
    Dict,
    Iterator,
    MutableMapping,
    Optional,
)


class Amalgam(ABC):
    """The abstract base class for language constructs."""

    @abstractmethod
    def evaluate(self, environment: Environment, *arguments: Any) -> Any:
        """
        Protocol for evaluating or unwrapping `Amalgam` objects.

        Given an `environment` and a list of optional `arguments`,
        evaluates or unwraps the `Amalgam` object.
        """


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

        elif self.parent is not None:
            return self.parent[item]

    def __setitem__(self, item: str, value: Amalgam) -> None:
        """Performs `__setitem__` on nested environments."""
        if self.ihas(item) or self.parent is None:
            self.iset(item, value)

        elif self.parent is not None:
            self.parent[item] = value

    def __delitem__(self, item: str) -> None:
        """Performs `__deltitem__` on nested environments."""
        if self.ihas(item) or self.parent is None:
            self.idel(item)

        elif self.parent is not None:
            del self.parent[item]

    def __contains__(self, item: object) -> bool:
        """Performs `__contains__` on nested environments."""
        if self.ihas(item) or self.parent is None:
            return self.ihas(item)

        elif self.parent is not None:
            return item in self.parent

    def __iter__(self) -> Iterator[str]:
        """Performs `__iter__` on nested environments."""
        if self.parent is None:
            return self.iiter()

        else:
            return iter(self.parent)

    def __len__(self) -> int:
        """Performs `__len__` on nested environments."""
        if self.parent is None:
            return self.ilen()

        else:
            return len(self.parent)

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
