from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from fractions import Fraction
from itertools import chain
from typing import (
    cast,
    Any,
    Callable,
    Dict,
    Iterator,
    Generic,
    MutableMapping,
    Optional,
    Tuple,
    TypeVar,
    Sequence,
    Union,
)


class Amalgam(ABC):
    """The abstract base class for language constructs."""

    @abstractmethod
    def evaluate(self, environment: Environment) -> Any:
        """
        Protocol for evaluating or unwrapping `Amalgam` objects.

        This is responsible for evaluating or reducing `Amalgam`
        objects given a specific `environment`. The `Function`
        subclass extends this method by binding the environment
        as an instance attribute `env`.
        """

    def bind(self, environment: Environment) -> Amalgam:  # pragma: no cover
        """
        Protocol for implementing environment binding for `Function`.

        This base implementation is responsible for allowing `bind`
        to be called on other `Amalgam` subclasses by performing
        no operation aside from returning `self`.
        """
        return self

    def call(
        self, environment: Environment, *arguments: Amalgam
    ) -> Amalgam:  # pragma: no cover
        """
        Protocol for implementing function calls for `Function`.

        This base implementation is responsible for making the
        type signature for the `func` attribute of `SExpression`
        to properly type check when the `evaluate` method is
        called.
        """
        raise NotImplementedError(f"{self.__class__.__name__} is not callable")

    def _make_repr(self, value: Any) -> str:  # pragma: no cover
        """Helper method for creating `__repr__` for subclasses."""
        return f"<{self.__class__.__name__} '{value!s}' @ {hex(id(self))}>"


@dataclass(repr=False)
class Atom(Amalgam):
    """An `Amalgam` that represents different atoms."""

    value: str

    def evaluate(self, _environment: Environment) -> Atom:
        return self

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(self.value)

    def __str__(self) -> str:
        return str(self.value)


@dataclass(repr=False, order=True)
class Numeric(Amalgam):
    """An `Amalgam` that wraps around numeric types."""

    value: Union[int, float, Fraction]

    def evaluate(self, _environment: Environment) -> Numeric:
        return self

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(self.value)

    def __str__(self) -> str:
        return str(self.value)


@dataclass(repr=False, order=True)
class String(Amalgam):
    """An `Amalgam` that wraps around strings."""

    value: str

    def evaluate(self, _environment: Environment) -> String:
        return self

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(f"\"{self.value}\"")

    def __str__(self) -> str:
        return f"\"{self.value}\""


@dataclass(repr=False)
class Symbol(Amalgam):
    """An `Amalgam` that wraps around symbols."""

    value: str

    def evaluate(self, environment: Environment) -> Amalgam:
        return environment[self.value]

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(self.value)

    def __str__(self) -> str:
        return self.value


@dataclass(repr=False)
class Function(Amalgam):
    """An `Amalgam` that wraps around functions."""

    name: str
    fn: Callable[..., Amalgam]
    defer: bool = False

    def __post_init__(self):
        self.env = cast(Environment, None)

    def evaluate(self, _environment: Environment) -> Function:
        return self

    def bind(self, environment: Environment) -> Function:
        self.env = environment
        return self

    def call(self, environment: Environment, *arguments: Amalgam) -> Amalgam:
        if self.env is not None:
            environment = self.env

        if self.defer:
            arguments = tuple(Quoted(arg) for arg in arguments)
        else:
            arguments = tuple(arg.evaluate(environment) for arg in arguments)

        return self.fn(environment, *arguments)

    def with_name(self, name: str) -> Function:
        self.name = name
        return self

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(self.name)

    def __str__(self) -> str:  # pragma: no cover
        return self.name


@dataclass(init=False, repr=False)
class SExpression(Amalgam):
    """An `Amalgam` that wraps around S-Expressions."""

    vals: Tuple[Amalgam, ...]

    def __init__(self, *vals: Amalgam) -> None:
        self.vals = vals

    @property
    def func(self) -> Amalgam:
        return self.vals[0]

    @property
    def args(self) -> Tuple[Amalgam, ...]:
        return self.vals[1:]

    def evaluate(self, environment: Environment) -> Amalgam:
        return self.func.evaluate(environment).call(environment, *self.args)

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(f"{self.func!r} {' '.join(map(repr, self.args))}")

    def __str__(self) -> str:
        return f"({' '.join(map(str, self.vals))})"


T = TypeVar("T", bound=Amalgam)


@dataclass(init=False, repr=False)
class Vector(Amalgam, Generic[T]):
    """An `Amalgam` that wraps around a homogenous vector."""

    vals: Tuple[T, ...]

    def __init__(self, *vals: T) -> None:
        self.vals = vals

    def evaluate(self, environment: Environment) -> Vector:
        return Vector(*(val.evaluate(environment) for val in self.vals))

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(" ".join(map(repr, self.vals)))

    def __str__(self) -> str:
        return f"[{' '.join(map(str, self.vals))}]"


@dataclass(repr=False)
class Quoted(Amalgam, Generic[T]):
    """An `Amalgam` that defers evaluation of other `Amalgam`s."""

    value: T

    def evaluate(self, _environment: Environment) -> Quoted:
        return self

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(repr(self.value))

    def __str__(self) -> str:
        return f"'{self.value!s}"


def create_fn(
    fname: str, fargs: Sequence[str], fbody: Amalgam, defer: bool = False
) -> Function:
    """Helper function for creating `Function` objects.

    Given the name of the function: `fname`, a sequence of argument
    names: `fargs`, and the `Amalgam` to be evaluated: `fbody`,
    creates a new `closure_fn` to be wrapped by a `Function`.
    """

    def closure_fn(environment: Environment, *arguments: Amalgam) -> Amalgam:
        """Callable responsible for evaluating `fbody`."""

        # Create a child environment and bind args to their names.
        # TODO: Raise an error when missing arguments instead.
        cl_env = environment.env_push(dict(zip(fargs, arguments)))

        # Call the `evaluate` method on the function body with
        # `cl_env` and then call `bind` on the result with the
        # same environment.
        return fbody.evaluate(cl_env).bind(cl_env)

    return Function(fname, closure_fn, defer)


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
