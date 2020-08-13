from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Amalgam(ABC):
    """The abstract base class for language constructs."""

    @abstractmethod
    def evaluate(self, environment: Any, *arguments: Any) -> Any:
        """
        Protocol for evaluating or unwrapping `Amalgam` objects.

        Given an `environment` and a list of optional `arguments`,
        evaluates or unwraps the `Amalgam` object.
        """
        raise NotImplementedError("`Amalgam` does not implement evaluation")
