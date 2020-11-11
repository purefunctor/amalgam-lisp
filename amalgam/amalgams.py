from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from fractions import Fraction
from io import StringIO
from typing import (
    cast,
    Any,
    Callable,
    Generic,
    Iterator,
    List,
    Mapping,
    NamedTuple,
    Sequence,
    Tuple,
    TypeVar,
    TYPE_CHECKING,
)


if TYPE_CHECKING:  # pragma: no cover
    from amalgam.environment import Environment


@dataclass
class Located:
    """
    The base dataclass for encapsulating location data of nodes.

    Provides an API similar to Lark's :class:`Token` class for
    convenience.

    Attributes:
      line_span (:class:`Tuple[int, int]`): Lines spanned by a node
      column_span (:class:`Tuple[int, int]`): Columns spanned by a node
    """

    line_span: Tuple[int, int] = field(
        init=False, compare=False, repr=False, default=(-1, -1),
    )

    column_span: Tuple[int, int] = field(
        init=False, compare=False, repr=False, default=(-1, -1),
    )

    @property
    def line(self) -> int:
        """The starting line number of a node."""
        return self.line_span[0]

    @property
    def end_line(self) -> int:
        """The ending line number of a node."""
        return self.line_span[1]

    @property
    def column(self) -> int:
        """The starting column number of a node."""
        return self.column_span[0]

    @property
    def end_column(self) -> int:
        """The ending column number of a node."""
        return self.column_span[1]

    def located_on(
        self,
        *,
        lines: Tuple[int, int] = (-1, -1),
        columns: Tuple[int, int] = (-1, -1),
    ) -> Located:
        """
        Helper method for setting :attr:`Located.line_span` and
        :attr:`Located.column_span`.
        """
        self.line_span = lines
        self.column_span = columns
        return self


class Amalgam(Located, ABC):
    """The abstract base class for language constructs."""

    @abstractmethod
    def evaluate(self, environment: Environment) -> Any:
        """
        Protocol for evaluating or unwrapping :class:`Amalgam` objects.
        """

    def bind(self, environment: Environment) -> Amalgam:  # pragma: no cover
        """
        Protocol for implementing environment binding for
        :class:`Function`.

        This base implementation is responsible for allowing `bind`
        to be called on other :class:`Amalgam` subclasses by
        performing no operation aside from returning :data:`self`.
        """
        return self

    def call(
        self, environment: Environment, *arguments: Amalgam
    ) -> Amalgam:  # pragma: no cover
        """
        Protocol for implementing function calls for
        :class:`Function`.

        This base implementation is responsible for making the type
        signature of :attr:`SExpression.func` to properly type check
        when :meth:`SExpression.evaluate` is called, as well as
        returning a fatal :class:`.Notification` for non-callable
        types.
        """
        if isinstance(self, Notification):
            notification = self
            value = Atom("call")
        else:
            notification = Notification()
            value = self

        notification.push(value, environment, "not a callable")
        return notification

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

    def evaluate(self, _environment: Environment) -> Atom:
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

    def evaluate(self, _environment: Environment) -> Numeric:
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

    def evaluate(self, _environment: Environment) -> String:
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

    def evaluate(self, environment: Environment) -> Amalgam:
        """
        Searches the provided `environment` fully with
        :attr:`Symbol.value`. Returns the :class:`.Amalgam` object
        bound to the :attr:`Symbol.value` in the environment. Returns
        a fatal :class:`.Notification` if a binding is not found.
        """
        try:
            with environment.search_at(depth=-1):
                return environment[self.value]
        except KeyError:
            notification = Notification()
            notification.push(self, environment, "unbound symbol")
            return notification

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(self.value)

    def __str__(self) -> str:
        return self.value


@dataclass(repr=False)
class Function(Amalgam):
    """
    An :class:`.Amalgam` that wraps around functions.

    Attributes:
      name (:class:`str`): The name of the function.

      fn (:class:`Callable[..., Amalgam]`): The function being wrapped.
        Must have the signature: `(env, amalgams...) -> amalgam`.

      defer (:class:`bool`): If set to :obj:`False`, arguments are
        evaluated before being passed to :attr:`Function.fn`.

      contextual (:class:`bool`): If set to :obj:`True`, disallows
        function calls when :attr:`.Function.in_context` is set to
        :obj:`False`.

      env (:class:`.environment.Environment`): The
        :class:`.environment.Environment` instance bound to the
        function. Overrides the `environment` parameter passed to the
        :meth:`.Function.call` method.

      in_context (:class:`bool`): Predicate that disallows functions
        to be called outside of specific contexts. Makes
        :meth:`.Function.call` return a fatal :class:`.Notification`
        when set to :obj:`False` and :attr:`.Function.contextual` is
        set to :obj:`True`.
    """

    name: str
    fn: Callable[..., Amalgam]
    defer: bool = False
    contextual: bool = False

    def __post_init__(self):
        self.env = cast("Environment", None)
        self.in_context = False

    def evaluate(self, _environment: Environment) -> Function:
        """Evaluates to the same :class:`.Function` reference."""
        return self

    def bind(self, environment: Environment) -> Function:
        """
        Sets the :attr:`.Function.env` attribute and returns the same
        :class:`.Function` reference.
        """
        self.env = environment
        return self

    def call(self, environment: Environment, *arguments: Amalgam) -> Amalgam:
        """
        Performs the call to the :attr:`.Function.fn` attribute.

        Performs pre-processing depending on the values of
        :attr:`.Function.defer`, :attr:`.Function.contextual`, and
        :attr:`.Function.in_context`,
        """
        if self.contextual and not self.in_context:
            notification = Notification()
            notification.push(self, environment, "invalid context")
            return notification

        if self.env is not None:
            environment = self.env

        args = []
        for argument in arguments:
            if not self.defer:
                argument = argument.evaluate(environment)
                if isinstance(argument, Notification):
                    if argument.fatal:
                        argument.push(
                            Atom(self.name), environment, "inherited",
                        )
                    return argument
            args.append(argument)

        return self.fn(environment, *args)

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

    def evaluate(self, environment: Environment) -> Amalgam:
        """
        Evaluates :attr:`func` using `environment` before invoking
        the :meth:`call` method with `environment` and
        :attr:`SExpression.args`.
        """
        result = self.func.evaluate(environment).call(environment, *self.args)
        if isinstance(result, Notification):
            if result.fatal:
                result.push(self, environment, "inherited")
        return result

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

    def evaluate(self, environment: Environment) -> Amalgam:
        """
        Creates a new :class:`.Vector` by evaluating every value in
        :attr:`Vector.vals`.
        """
        vals = []
        for val in self.vals:
            val = val.evaluate(environment)
            if isinstance(val, Notification):
                if val.fatal:
                    val.push(self, environment, "inherited")
                return val
            vals.append(val)
        return Vector(*vals)

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

    def evaluate(self, _environment: Environment) -> Quoted:
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

    def evaluate(self, _environment: Environment) -> Internal:
        """Evaluates to the same :class:`.Internal` reference."""
        return self

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(repr(self.value))

    def __str__(self) -> str:  # pragma: no cover
        return f"~{self.value!s}~"


class Trace(NamedTuple):
    """Encapsulates information for tracking notifications."""
    amalgam: Amalgam
    environment: Environment
    message: str


@dataclass(init=False, repr=False)
class Notification(Amalgam):
    """
    An :class:`Amalgam` that encapsulates and tracks notifications.

    Attributes:
      fatal (:class:`bool`): Specifies whether the notification should
        unconditionally propagate and halt evaluation.
      payload (:class:`Amalgam`): An optional payload to be carried by
        a notification.
      trace (:class:`List[Trace]`): A stack of :class:`.Trace` objects
        that tell how the notification propagated.
    """

    def __init__(
        self, *, fatal: bool = True, payload: Amalgam = Atom("NIL"),
    ) -> None:
        self.fatal = fatal
        self.payload = payload
        self.trace: List[Trace] = []

    def evaluate(self, _environment: Environment) -> Notification:
        """Evaluates to the same :class:`.Notification` reference."""
        return self

    def push(
        self, amalgam: Amalgam, environment: Environment, message: str,
    ) -> None:
        """Pushes a :class:`.Trace` into :attr:`Notification.trace`."""
        self.trace.append(Trace(amalgam, environment, message))

    def pop(self) -> Trace:
        """Pops a :class:`.Trace` from :attr:`Notification.trace`."""
        return self.trace.pop()

    def make_report(
        self, text: str, source: str = "<unknown>"
    ) -> str:  # pragma: no cover
        """
        Generates a report to be printed to :data:`sys.stderr`.

        Accepts :data:`text` and :data:`source` for prettified output.
        """
        trace = []
        for a, e, m in self.trace:
            if isinstance(a, Atom):
                continue
            if a.line_span == (-1, -1) or a.column_span == (-1, -1):
                continue
            trace.append((a, e, m))
            if isinstance(a, (SExpression, Vector)):
                break

        lines = text.splitlines()

        if len(trace) > 1:
            (atom_a, atom_e, atom_m), *_, (expr_a, _, _) = trace

            snippets = lines[expr_a.line - 1:expr_a.end_line]
            _code_block = []
            for line_no, snippet in enumerate(snippets, start=expr_a.line):
                padding = 6 - len(str(line_no))
                _code_block.append(f"{line_no:>{padding}} | {snippet}")
            code_block = "\n".join(_code_block)

        else:
            (atom_a, atom_e, atom_m), *_ = trace

            snippet = lines[atom_a.line - 1]
            padding = 6 - len(str(atom_a.line))
            code_block = f"{atom_a.line:>{padding}} | {snippet}"

        line_span = f"{atom_a.line}~{atom_a.end_line}"
        column_span = f"{atom_a.column}~{atom_a.end_column}"
        message = f"{atom_a!s} ~ {atom_m}"
        environment = atom_e.name

        report = StringIO()
        report.write(
            f"In file \"{source}\" "
            f"near lines {line_span}, columns {column_span}\n"
            f"      |\n"
            f"{code_block}\n"
            f"      |\n"
            f"      Message: {message}, Environment: {environment}\n"
        )
        report.seek(0)
        return report.read()

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(
            f"fatal={self.fatal}, payload={self.payload}, trace={self.trace}"
        )

    def __iter__(self) -> Iterator[Trace]:
        return reversed(self.trace)


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

    def closure_fn(environment: Environment, *arguments: Amalgam) -> Amalgam:
        """Callable responsible for evaluating `fbody`."""

        # Create a child environment and bind args to their names.
        # TODO: Raise an error when missing arguments instead.
        cl_env = environment.env_push(
            dict(zip(fargs, arguments)), f"{fname}-closure",
        )

        # Call the `evaluate` method on the function body with
        # `cl_env` and then call `bind` on the result with the
        # same environment.
        return fbody.evaluate(cl_env).bind(cl_env)

    return Function(fname, closure_fn, defer, contextual)
