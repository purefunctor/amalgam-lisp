from amalgam.amalgams import *


def amalgam_ast_to_python(x: Amalgam) -> object:
    """Unwraps the values encapsulated by AST objects."""
    if isinstance(x, (Numeric, Symbol, String, Atom)):
        return x.value
    elif isinstance(x, (SExpression, Vector)):
        return list(map(amalgam_ast_to_python, x))
