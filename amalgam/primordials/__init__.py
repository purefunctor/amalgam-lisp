from amalgam.primordials.arithmetic import (  # noqa: F401
    _add, _sub, _mul, _div, ARITHMETIC,
)
from amalgam.primordials.boolean import (  # noqa: F401
    _bool, _not, _and, _or, BOOLEAN,
)
from amalgam.primordials.comparison import (  # noqa: F401
    _gt, _lt, _eq, _ne, _ge, _le, COMPARISON,
)
from amalgam.primordials.control import (  # noqa: F401
    _if, _when, _cond, _do, _loop, CONTROL,
)
from amalgam.primordials.io import (  # noqa: F401
    _print, _putstrln, _exit, IO_Store,
)
from amalgam.primordials.meta import (  # noqa: F401
    _setn, _setr, _unquote, _eval, _fn, _mkfn, _macro, _let, META,
)
from amalgam.primordials.string import (  # noqa: F401
    _concat, STRING,
)
from amalgam.primordials.vector import (  # noqa: F401
    _merge, _slice, _at, _remove, _len, _cons, _snoc,
    _is_map, _map_in, _map_at, _map_up, VECTOR,
)


FUNCTIONS = {
    **ARITHMETIC,
    **BOOLEAN,
    **COMPARISON,
    **CONTROL,
    **IO_Store,
    **META,
    **VECTOR,
}
