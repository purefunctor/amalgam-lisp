from prompt_toolkit import PromptSession

from amalgam.amalgams import Environment
from amalgam.primordials import FUNCTIONS
from amalgam.parser import AmalgamParser


class Engine:

    def __init__(
        self, *, prompt: str = "> ", prompt_cont: str = "| ",
    ) -> None:

        self.prompt = prompt
        self.prompt_cont = prompt_cont

        self.parser = AmalgamParser()
        self.environment = Environment(FUNCTIONS)

    def repl(self) -> None:
        cont = False
        session = PromptSession()

        while True:
            try:
                prompt = self.prompt if not cont else self.prompt_cont

                text = session.prompt(prompt)

                if cont:
                    text = "\n" + text

                with self.parser.as_repl_parser():
                    expr = self.parser.parse(text)

                if expr is not None:
                    print(expr.evaluate(self.environment))
                    cont = False
                else:
                    cont = True

            except EOFError:
                self.parser.parse("(exit)").evaluate(self.environment)

            except Exception as e:
                if cont:
                    cont = False
                print(f"{e.__class__.__qualname__}: {e}")
