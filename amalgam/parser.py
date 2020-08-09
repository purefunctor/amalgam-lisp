import parsy


IDENTIFIER_PATTERN = r"(?![0-9'])[\+\-\*/\\&<=>?!_a-zA-Z0-9']+"


@parsy.generate
def numeric_literal():
    """Parses a given numeric literal"""

    integral_parser = parsy.regex(r"-?(0|[1-9][0-9]*)")

    floating_parser = parsy.seq(
        parsy.string("."),
        parsy.regex("[0-9]+"),
    ).map("".join)

    fraction_parser = parsy.seq(
        parsy.string("/"),
        integral_parser,
    ).map("".join)

    head = yield integral_parser
    tail = yield (floating_parser | fraction_parser).optional()

    return head if tail is None else head + tail


@parsy.generate
def s_expression():
    """Parses a given S-Expression"""

    l_paren = yield parsy.string("(")

    f = yield parsy.regex(IDENTIFIER_PATTERN)

    yield parsy.whitespace

    v = yield (numeric_literal | s_expression).sep_by(parsy.whitespace)

    r_paren = yield parsy.string(")")

    return [l_paren, f, *v, r_paren]
