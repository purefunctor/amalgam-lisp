import parsy


IDENTIFIER_PATTERN = r"(?![0-9'])[\+\-\*/\\&<=>?!_a-zA-Z0-9']+"
NUMERIC_PATTERN = r"(0|[1-9][0-9]*)((\.[0-9]+)|(/(0|[1-9][0-9]*)))?"


@parsy.generate
def s_expression():
    """Parses a given S-Expression"""

    l_paren = yield parsy.string("(")

    f = yield parsy.regex(IDENTIFIER_PATTERN)

    yield parsy.whitespace

    v = yield (parsy.regex(NUMERIC_PATTERN) | s_expression).sep_by(parsy.whitespace)

    r_paren = yield parsy.string(")")

    return [l_paren, f, *v, r_paren]