import io
import sys

import click

import amalgam.engine as en


@click.command()
@click.argument("file", required=False, type=click.File("r"))
@click.option("-e", "--expr", default=None, help="Expression to evaluate.")
def amalgam_main(file, expr):
    has_file = file is not None
    has_expr = expr is not None

    if has_file and has_expr:
        raise click.BadParameter("Cannot use FILE and --expr together")

    elif not has_file and not has_expr:
        en.Engine().repl()  # Guarantees SystemExit

    if has_file:
        text = file.read()
        source = f"<{file.name}>"

    elif has_expr:  # pragma: no branch
        text = expr
        source = "<expr-parameter>"

    en.Engine().interpret(
        text, source, io.StringIO() if has_file else sys.stdout
    )
