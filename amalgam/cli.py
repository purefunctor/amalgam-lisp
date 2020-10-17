import click

from amalgam.amalgams import Environment
from amalgam.parser import AmalgamParser
from amalgam.primordials import FUNCTIONS
from amalgam.repl import AmalgamREPL


@click.command()
@click.argument("file", required=False, type=click.File("r"))
@click.option("-e", "--expr", default=None, help="Expression to evaluate.")
def amalgam_main(file, expr):
    has_file = file is not None
    has_expr = expr is not None

    if not has_file and not has_expr:
        AmalgamREPL().repl()  # Guarantees SystemExit

    elif has_file and not has_expr:
        text = file.read()

    elif not has_file and has_expr:
        text = expr

    else:
        raise click.BadParameter("Cannot use FILE and --expr together")

    env = Environment(None, FUNCTIONS.copy())
    print(AmalgamParser().parse(text).evaluate(env))
