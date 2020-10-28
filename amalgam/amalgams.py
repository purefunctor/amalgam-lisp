from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from fractions import Fraction
from typing import (
    cast,
    Any,
    Callable,
    Generic,
    Mapping,
    Sequence,
    Tuple,
    TypeVar,
)

import amalgam.environment as ev


class Amalgam(ABC):
    """The abstract base class for language constructs."""

    @abstractmethod
    def evaluate(self, environment: ev.Environment) -> Any:
        """
        Protocol for evaluating or unwrapping :class:`Amalgam` objects.
        """

    def bind(self, environment: ev.Environment) -> Amalgam:  # pragma: no cover
        """
        Protocol for implementing environment binding for
        :class:`Function`.

        This base implementation is responsible for allowing `bind`
        to be called on other :class:`Amalgam` subclasses by
        performing no operation aside from returning :data:`self`.
        """
        return self

    def call(
        self, environment: ev.Environment, *arguments: Amalgam
    ) -> Amalgam:  # pragma: no cover
        """
        Protocol for implementing function calls for
        :class:`Function`.

        This base implementation is responsible for making the type
        signature of :attr:`SExpression.func` to properly type check
        when :meth:`SExpression.evaluate` is called, as well as raising
        :class:`NotImplementedError` for non-callable types.
        """
        raise NotImplementedError(f"{self.__class__.__name__} is not callable")

    def _make_repr(self, value: Any) -> str:  # pragma: no cover
        """Helper method for creating a :meth:`__repr__`."""
        return f"<{self.__class__.__name__} '{value!s}' @ {hex(id(self))}>"


@dataclass(repr=False)
class Atom(Amalgam):
    """
    An :class:`.Amalgam` that represents different atoms.

    Attributes:
      value (:class:`str`): The name of the atom.
    """

    value: str

    def evaluate(self, _environment: ev.Environment) -> Atom:
        """Evaluates to the same :class:`.Atom` reference."""
        return self

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(self.value)

    def __str__(self) -> str:
        return f":{self.value}"


N = TypeVar("N", int, float, Fraction)


@dataclass(repr=False, order=True)
class Numeric(Amalgam, Generic[N]):
    """
    An :class:`.Amalgam` that wraps around numeric types.

    Parameterized as a :class:`Generic` by:
    :data:`N = TypeVar("N", int, float, Fraction)`

    Attributes:
      value (:data:`N`): The numeric value being wrapped.
    """

    value: N

    def evaluate(self, _environment: ev.Environment) -> Numeric:
        """Evaluates to the same :class:`.Numeric` reference."""
        return self

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(self.value)

    def __str__(self) -> str:
        return str(self.value)


@dataclass(repr=False, order=True)
class String(Amalgam):
    """
    An :class:`.Amalgam` that wraps around strings.

    Attributes:
      value (:class:`str`): The string being wrapped.
    """

    value: str

    def evaluate(self, _environment: ev.Environment) -> String:
        """Evaluates to the same :class:`.String` reference."""
        return self

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(f"\"{self.value}\"")

    def __str__(self) -> str:
        return f"\"{self.value}\""


@dataclass(repr=False)
class Symbol(Amalgam):
    """
    An :class:`.Amalgam` that wraps around symbols.

    Attributes:
      value (:class:`str`): The name of the symbol.
    """

    value: str

    def evaluate(self, environment: ev.Environment) -> Amalgam:
        """
        Searches the provided `environment` fully with
        :attr:`Symbol.value`. Returns the :class:`.Amalgam` object
        bound to the :attr:`Symbol.value` in the environment. Raises
        :class:`.environment.SymbolNotFound` if a binding is not found.
        """
        with environment.search_at(depth=-1):
            return environment[self.value]

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(self.value)

    def __str__(self) -> str:
        return self.value


class DisallowedContextError(Exception):
    """Raised on functions outside of their intended contexts."""


@dataclass(repr=False)
class Function(Amalgam):
    """
    An :class:`.Amalgam` that wraps around functions.

    Attributes:
      name (:class:`str`): The name of the function.

      fn (:class:`Callable[..., Amalgam]`): The function being wrapped.
        Must have the signature: `(env, amalgams...) -> amalgam`.

      defer (:class:`bool`): If set to :obj:`True`, arguments are
        wrapped in :class:`.Quoted` before being passed to
        :attr:`.Function.fn`.

      contextual (:class:`bool`): If set to :obj:`True`, disallows
        function calls when :attr:`.Function.in_context` is set to
        :obj:`False`.

      env (:class:`.environment.Environment`): The
        :class:`.environment.Environment` instance bound to the
        function. Overrides the `environment` parameter passed to the
        :meth:`.Function.call` method.

      in_context (:class:`bool`): Predicate that disallows functions
        to be called outside of specific contexts. Makes
        :meth:`.Function.call` raise :class:`.DisallowedContextError`
        when set to :obj:`False` and :attr:`.Function.contextual` is
        set to :obj:`True`.
    """

    name: str
    fn: Callable[..., Amalgam]
    defer: bool = False
    contextual: bool = False

    def __post_init__(self):
        self.env = cast(ev.Environment, None)
        self.in_context = False

    def evaluate(self, _environment: ev.Environment) -> Function:
        """Evaluates to the same :class:`.Function` reference."""
        return self

    def bind(self, environment: ev.Environment) -> Function:
        """
        Sets the :attr:`.Function.env` attribute and returns the same
        :class:`.Function` reference.
        """
        self.env = environment
        return self

    def call(self, environment: ev.Environment, *arguments: Amalgam) -> Amalgam:
        """
        Performs the call to the :attr:`.Function.fn` attribute.

        Performs pre-processing depending on the values of
        :attr:`.Function.defer`, :attr:`.Function.contextual`, and
        :attr:`.Function.in_context`,
        """
        if self.contextual and not self.in_context:
            raise DisallowedContextError(f"invalid context for {self.name}")

        if self.env is not None:
            environment = self.env

        if self.defer:
            arguments = tuple(Quoted(arg) for arg in arguments)
        else:
            arguments = tuple(arg.evaluate(environment) for arg in arguments)

        return self.fn(environment, *arguments)

    def with_name(self, name: str) -> Function:
        """
        Sets the :attr:`.Function.name` attribute and returns the same
        :class:`.Function` reference.
        """
        self.name = name
        return self

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(self.name)

    def __str__(self) -> str:  # pragma: no cover
        return self.name


@dataclass(init=False, repr=False)
class SExpression(Amalgam):
    """
    An :class:`.Amalgam` that wraps around S-Expressions.

    Attributes:
      vals (:class:`Tuple[Amalgam, ...]`): Entities contained by the
        S-Expression.
    """

    vals: Tuple[Amalgam, ...]

    def __init__(self, *vals: Amalgam) -> None:
        self.vals = vals

    @property
    def func(self) -> Amalgam:
        """The head of the :attr:`SExpression.vals`."""
        return self.vals[0]

    @property
    def args(self) -> Tuple[Amalgam, ...]:
        """The rest of the :attr:`SExpression.vals`."""
        return self.vals[1:]

    def evaluate(self, environment: ev.Environment) -> Amalgam:
        """
        Evaluates :attr:`func` using `environment` before invoking
        the :meth:`call` method with `environment` and
        :attr:`SExpression.args`.
        """
        return self.func.evaluate(environment).call(environment, *self.args)

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(f"{self.func!r} {' '.join(map(repr, self.args))}")

    def __str__(self) -> str:
        return f"({' '.join(map(str, self.vals))})"


T = TypeVar("T", bound=Amalgam)


@dataclass(init=False, repr=False)
class Vector(Amalgam, Generic[T]):
    """
    An :class:`.Amalgam` that wraps around a homogenous vector.

    Parameterized as a :class:`Generic` by:
    :data:`T = TypeVar("T", bound=Amalgam)`

    Attributes:
      vals (:class:`Tuple[T, ...]`): Entities contained by the vector

      mapping (:class:`Mapping[str, Amalgam]`): Mapping representing
        vectors with :class:`.Atom` s for odd indices and
        :class:`.Amalgam` s for even indices.
    """

    vals: Tuple[T, ...]

    def __init__(self, *vals: T) -> None:
        self.vals = vals
        self.mapping = self._as_mapping()

    def evaluate(self, environment: ev.Environment) -> Vector:
        """
        Creates a new :class:`.Vector` by evaluating every value in
        :attr:`Vector.vals`.
        """
        return Vector(*(val.evaluate(environment) for val in self.vals))

    def _as_mapping(self) -> Mapping[str, Amalgam]:
        """
        Attemps to create a :class:`Mapping[str, Amalgam]` from
        :attr:`Vector.vals`.

        Odd indices must be :class:`.Atom` s and even indices must be
        :class:`.Amalgam` s. Returns an empty mapping if this form is
        not met.
        """
        if len(self.vals) % 2 != 0 or len(self.vals) == 0:
            return {}

        mapping = {}

        atoms = self.vals[::2]
        amalgams = self.vals[1::2]

        for atom, amalgam in zip(atoms, amalgams):
            if not isinstance(atom, Atom):
                return {}
            mapping[atom.value] = amalgam

        return mapping

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(" ".join(map(repr, self.vals)))

    def __str__(self) -> str:
        return f"[{' '.join(map(str, self.vals))}]"


@dataclass(repr=False)
class Quoted(Amalgam, Generic[T]):
    """
    An :class:`Amalgam` that defers evaluation of other
    :class:`Amalgam` s.

    Parameterized as a :class:`Generic` by:
    :data:`T = TypeVar("T", bound=Amalgam)`

    Attributes:
      value (:data:`T`): The :class:`.Amalgam` being deferred.
    """

    value: T

    def evaluate(self, _environment: ev.Environment) -> Quoted:
        """Evaluates to the same :class:`.Quoted` reference."""
        return self

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(repr(self.value))

    def __str__(self) -> str:
        return f"'{self.value!s}"


P = TypeVar("P", bound=object)


@dataclass(repr=False)
class Internal(Amalgam, Generic[P]):
    """
    An :class:`Amalgam` that holds Python :class:`object` s.

    Parameterized as a :class:`Generic` by:
    :data:`P = TypeVar("P", bound=object)`

    Attributes:
      value (:data:`P`): The Python :class:`object` being wrapped.
    """

    value: P

    def evaluate(self, _environment: ev.Environment) -> Internal:
        """Evaluates to the same :class:`.Internal` reference."""
        return self

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(repr(self.value))

    def __str__(self) -> str:  # pragma: no cover
        return f"~{self.value!s}~"


def create_fn(
    fname: str,
    fargs: Sequence[str],
    fbody: Amalgam,
    defer: bool = False,
    contextual: bool = False,
) -> Function:
    """Helper function for creating `Function` objects.

    Given the name of the function: `fname`, a sequence of argument
    names: `fargs`, and the `Amalgam` to be evaluated: `fbody`,
    creates a new `closure_fn` to be wrapped by a `Function`.
    """

    def closure_fn(environment: ev.Environment, *arguments: Amalgam) -> Amalgam:
        """Callable responsible for evaluating `fbody`."""

        # Create a child environment and bind args to their names.
        # TODO: Raise an error when missing arguments instead.
        cl_env = environment.env_push(dict(zip(fargs, arguments)))

        # Call the `evaluate` method on the function body with
        # `cl_env` and then call `bind` on the result with the
        # same environment.
        return fbody.evaluate(cl_env).bind(cl_env)

    return Function(fname, closure_fn, defer, contextual)
