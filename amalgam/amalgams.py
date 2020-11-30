from __future__ import annotations

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from functools import wraps
from fractions import Fraction
from io import StringIO
from itertools import chain
from typing import (
    cast,
    Any,
    Callable,
    Generic,
    Iterator,
    List,
    Mapping,
    Sequence,
    Tuple,
    TypeVar,
    TYPE_CHECKING,
)


if TYPE_CHECKING:  # pragma: no cover
    from amalgam.environment import Environment


L = TypeVar("L", bound="Located")


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
        self: L,
        *,
        lines: Tuple[int, int] = (-1, -1),
        columns: Tuple[int, int] = (-1, -1),
    ) -> L:
        """
        Helper method for setting :attr:`Located.line_span` and
        :attr:`Located.column_span`.
        """
        self.line_span = lines
        self.column_span = columns
        return self


class Failure(Exception):
    """
    Represents failures during evaluation.

    Attribute:
      amalgam (:class:`Amalgam`): The :class:`Amalgam` where evaluation
        failed.

      environment (:class:`Environment`): The execution environment
        used to evaluate :data:`amalgam`.

      message (:class:`str`): An error message attached to the failure.
    """

    def __init__(
        self, amalgam: Amalgam, environment: Environment, message: str
    ) -> None:
        self.amalgam = amalgam
        self.environment = environment
        self.message = message


class FailureStack(Exception):
    """
    Represents a collection of :class:`Failure`s.

    Attributes:
      failures (:class:`List[Failure]`): A stack of :class:`Failure`
        objects.
    """

    def __init__(self, failures: List[Failure]) -> None:
        self.failures = failures

    def push(self, failure: Failure) -> None:
        """Pushes a :class:`Failure` into the :attr:`failures` stack."""
        self.failures.append(failure)

    @property
    def unpacked_failures(self) -> Iterator[Tuple[Amalgam, Environment, str]]:
        """Helper property for unpacking :class:`Failure`s."""
        for failure in self.failures:
            yield (failure.amalgam, failure.environment, failure.message)

    def make_report(
        self, text: str, source: str = "<unknown>"
    ) -> str:  # pragma: no cover
        """
        Generates a report to be printed to :data:`sys.stderr`.

        Accepts :data:`text` and :data:`source` for prettified output.
        """

        lines = text.splitlines()

        if len(self.failures) > 1:
            (atom_a, atom_e, atom_m), *_, (expr_a, _, _) = self.unpacked_failures

            snippets = lines[expr_a.line - 1:expr_a.end_line]
            _code_block = []
            for line_no, snippet in enumerate(snippets, start=expr_a.line):
                padding = 6 - len(str(line_no))
                _code_block.append(f"{line_no:>{padding}} | {snippet}")
            code_block = "\n".join(_code_block)

        else:
            (atom_a, atom_e, atom_m), *_ = self.unpacked_failures

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


class AmalgamMeta(ABCMeta):
    """
    Metaclass used to build :class:`Amalgam` subclasses.

    Allows for customized pre and post method execution behaviour, such
    as logging calls or tracking exceptions, effectively reducing
    boilerplate code.
    """

    def __new__(cls, name, bases, namespace):

        namespace["__evaluate"] = namespace["evaluate"]

        @wraps(namespace["__evaluate"])
        def evaluate(self: Amalgam, environment: Environment) -> Amalgam:
            try:
                return namespace["__evaluate"](self, environment)
            except Failure as f:
                raise FailureStack([f])
            except FailureStack as s:
                s.push(Failure(self, environment, "inherited"))
                raise
            except Exception:
                raise

        namespace["evaluate"] = evaluate

        return super().__new__(cls, name, bases, namespace)


class Amalgam(Located, metaclass=AmalgamMeta):
    """The abstract base class for language constructs."""

    @abstractmethod
    def evaluate(self, environment: Environment) -> Any:
        """
        Protocol for evaluating or unwrapping :class:`Amalgam` objects.
        """

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
            raise Failure(self, environment, "unbound symbol")

    def __repr__(self) -> str:  # pragma: no cover
        return self._make_repr(self.value)

    def __str__(self) -> str:
        return self.value


class InvalidContextError(Exception):
    """
    Raised when calling a :class:`Function` in invalid contexts.

    Attributes:
      environment (:class:`Environment`): The environment used in
        calling the :class:`Function`.
    """

    def __init__(self, environment: Environment) -> None:
        self.environment = environment


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

    env: Environment = field(
        init=False, compare=False, default=cast("Environment", None)
    )
    in_context: bool = field(init=False, compare=False, default=False)

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
        if self.env is not None:
            environment = self.env

        if self.contextual and not self.in_context:
            raise InvalidContextError(environment)

        args = [
            argument if self.defer else argument.evaluate(environment)
            for argument in arguments
        ]

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
        head = self.func.evaluate(environment)
        if isinstance(head, Function):
            try:
                return head.call(environment, *self.args)
            except InvalidContextError as e:
                # Instead of raising Failure with the Function instance,
                # we try to reconstruct a sensible Failure using func,
                # assuming that it's an AST node that we can use for
                # error reporting.
                raise FailureStack(
                    [Failure(self.func, e.environment, "invalid context")],
                )
        else:
            raise FailureStack([Failure(head, environment, "not a callable")])

    def __iter__(self) -> Iterator[Amalgam]:
        return iter(self.vals)

    def __len__(self) -> int:
        return len(self.vals)

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

    def __iter__(self) -> Iterator[T]:
        return iter(self.vals)

    def __len__(self) -> int:
        return len(self.vals)

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


def create_fn(
    fname: str,
    fargs: Sequence[str],
    fbody: Amalgam,
    defer: bool = False,
    contextual: bool = False,
) -> Function:
    """
    Helper function for creating :class:`Function` objects.

    Given the name of the function: :data:`fname`, a sequence of
    argument names: :data:`fargs`, and the :class:`Amalgam` to be
    evaluated: :data:`fbody`, creates a new :data:`closure_fn` to be
    wrapped by a :class:`Function`.

    :data:`fargs` can include :data:`&rest` to signify variadic
    arguments, and can be used in the following forms.

    Variadic for all arguments
    (λ [&rest]-> [&rest]) 1 2 3 == [[1 2 3]]

    Non-variadic for first :data:`n` arguments
    (λ [x &rest] -> [x &rest]) 1 2 3 == [1 [2 3]]

    Non-variadic for last :data:`n` arguments
    (λ [&rest x] -> [&rest x]) 1 2 3 == [[1 2] 3]

    Non-variadic for first :data:`n` and last:data:`m` arguments
    (λ [x &rest y] -> [x &rest y]) 1 2 3 == [1 [2] 3]
    """

    def closure_fn(environment: Environment, *arguments: Amalgam) -> Amalgam:
        """Callable responsible for evaluating `fbody`."""

        try:
            l_count = fargs.index("&rest")
            r_count = len(fargs) - l_count - 1

            l_names = zip(fargs[:l_count], arguments[:l_count])

            if r_count == 0:
                bindings = dict(l_names)
                bindings["&rest"] = Vector(*arguments[l_count:])
            else:
                r_names = zip(fargs[-r_count:], arguments[-r_count:])
                m_name = ("&rest", Vector(*arguments[l_count:-r_count]))
                bindings = dict(chain(l_names, (m_name,), r_names))

        except ValueError:
            bindings = dict(zip(fargs, arguments))

        cl_env = environment.env_push(bindings, f"{fname}-closure")

        result = fbody.evaluate(cl_env)
        if isinstance(result, Function):
            return result.bind(cl_env)
        else:
            return result

    return Function(fname, closure_fn, defer, contextual)
