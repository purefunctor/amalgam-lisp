from __future__ import annotations

from contextlib import contextmanager
from typing import (
    cast,
    Dict,
    Mapping,
    Optional,
    TYPE_CHECKING,
)


if TYPE_CHECKING:  # pragma: no cover
    from amalgam.amalgams import Amalgam
    from amalgam.engine import Engine

    Bindings = Mapping[str, Amalgam]


class TopLevelPop(Exception):
    """Raised at :meth:`Environment.env_pop`."""


class Environment:
    """
    Class that manages and represents nested execution environments.

    Attributes:
      bindings (:class:`Dict[str, Amalgam]`): A mapping of
        :class:`str` keys to :class:`.amalgams.Amalgam` values.

      parent (:class:`Optional[Environment]`): The parent
        :class:`Environment` instance to search into, forming a
        linked list.

      level (:class:`int`): The current length of the
        :class:`Environment` linked list. If a
        :attr:`~.Environment.parent` is provided, sets the current
        value to the parent's :attr:`~.Environment.level` + 1.

      search_depth (:class:`int`): The search depth when traversing
        the :class:`Environment` linked list in the
        :meth:`~.Environment.__contains__`,
        :meth:`~.Environment.__delitem__`,
        :meth:`~.Environment.__getitem__`, and
        :meth:`~.Environment.__setitem__` methods.

      name (:class:`str`): The name of the execution environment.

      engine (:class:`Engine`): A reference to the engine managing the
        :class:`.parser.Parser` instance and the global
        :class:`.Environment` instance.
    """

    def __init__(
        self,
        bindings: Bindings = None,
        parent: Environment = None,
        name: str = "unknown",
        engine: Engine = None,
    ) -> None:
        self.bindings: Dict[str, Amalgam] = {**bindings} if bindings else {}
        self.parent: Optional[Environment] = parent
        self.level: int = parent.level + 1 if parent else 0
        self.search_depth: int = 0
        self.name = name
        self.engine = cast("Engine", engine)

    def __getitem__(self, item: str) -> Amalgam:
        """
        Attempts to recursively obtain the provided `item`.

        Searches with respect to the current :attr:`search_depth` of the
        calling :class:`Environment` instance. If an existing `item`
        is encountered at a certain depth less than the target depth,
        returns that `item`, otherwise, raises :class:`SymbolNotFound`.
        """
        _self = self

        if self.search_depth >= 0:
            depth = self.search_depth + 1
        else:
            depth = self.level + 1

        # Search until the top-most environment,
        # raise SymbolNotFound otherwise.
        for _ in range(depth):
            try:
                return _self.bindings[item]
            except KeyError:
                _self = cast(Environment, _self.parent)
        else:
            raise KeyError(item)

    def __setitem__(self, item: str, value: Amalgam) -> None:
        """
        Attempts to recursively set the provided `value` to an `item`.

        Searches with respect to the current :attr:`search_depth` of the
        calling :class:`Environment` instance. If an existing `item` is
        encountered at a certain depth less than the target depth,
        overrides that `item` instead.
        """
        _self = self

        if self.search_depth >= 0:
            depth = self.search_depth
        else:
            depth = self.level

        # Search until the second-to-last environment,
        # set at the top-most environment otherwise.
        for _ in range(depth):
            if item in _self.bindings:
                _self.bindings[item] = value
                break
            else:
                _self = cast(Environment, _self.parent)
        else:
            _self.bindings[item] = value

    def __delitem__(self, item: str) -> None:
        """
        Attempts to recursively delete the provided `item`.

        Searches with respect to the current :attr:`search_depth` of the
        calling :class:`Environment` instance. If an existing `item` is
        encountered at a certain depth less than the target depth,
        deletes that `item` instead.
        """
        _self = self

        if self.search_depth >= 0:
            depth = self.search_depth + 1
        else:
            depth = self.level + 1

        # Search until the top-most environment,
        # raise SymbolNotFound otherwise.
        for _ in range(depth):
            try:
                del _self.bindings[item]
                break
            except KeyError:
                _self = cast(Environment, _self.parent)
        else:
            raise KeyError(item)

    def __contains__(self, item: str) -> bool:
        """
        Recursively checks whether an `item` exists.

        Searches with respect to the current :attr:`search_depth` of the
        calling :class:`Environment` instance. If the target `item` is
        encountered at a certain depth less than the target depth,
        immediately returns `True`, otherwise, returns `False`.
        """
        _self = self

        if self.search_depth >= 0:
            depth = self.search_depth + 1
        else:
            depth = self.level + 1

        # Search until an `item` is found,
        # return False otherwise
        for _ in range(depth):
            if item in _self.bindings:
                return True
            else:
                _self = cast(Environment, _self.parent)
        else:
            return False

    @contextmanager
    def search_at(self, *, depth=0):
        """
        Context manager for temporarily setting the lookup depth.

        The provided `depth` argument must not exceed the :attr:`level`
        of the calling :class:`Environment` instance, and will raise a
        :class:`ValueError` if done so.

        >>> env = Environment(FUNCTIONS)
        >>>
        >>> with env.search_at(depth=42):
        ...     env["+"]  # Raises ValueError

        Any negative integer can be passed as a `depth` to signify
        an infinite lookup until the top-most environment.

        >>> env = Environment(FUNCTIONS)
        >>> cl_env = env.env_push({...})
        >>>
        >>> with cl_env.search_at(depth=-1):
        ...    cl_env["+"]  # Searches `env`
        """
        if depth > self.level:
            exc = ValueError(
                f"depth {depth} is greater than maximum level {self.level}"
            )
            raise exc

        self.search_depth = depth

        try:
            yield self
        finally:
            self.search_depth = 0

    def env_push(self, bindings: Bindings = None, name: str = None) -> Environment:
        """
        Creates a new :class:`Environment` and binds the calling
        instance as its parent environment.
        """
        if name is None:
            name = f"{self.name}-child"
        return Environment(
            bindings=bindings, parent=self, name=name, engine=self.engine,
        )

    def env_pop(self) -> Environment:
        """
        Discards the current :class:`Environment` and returns the parent
        :class:`Environment`.
        """
        if self.parent is not None:
            return self.parent
        else:
            raise TopLevelPop("cannot discard top-level Environment")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Environment \"name={self.name}\" @ {hex(id(self))}>"
