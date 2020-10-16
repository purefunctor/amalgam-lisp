from prompt_toolkit import PromptSession

from amalgam.amalgams import Environment
from amalgam.primordials import FUNCTIONS
from amalgam.parser import AmalgamParser


class AmalgamREPL:

    def __init__(
        self, prompt: str = "> ", prompt_cont: str = "| ",
    ) -> None:

        self.prompt = prompt
        self.prompt_cont = prompt_cont

        self.repl_parser = AmalgamParser()
        self.session = PromptSession()

        self.environment = Environment(None, FUNCTIONS.copy())

    def repl(self) -> None:
        cont = False

        while True:
            try:
                prompt = self.prompt if not cont else self.prompt_cont

                text = self.session.prompt(prompt)

                if cont:
                    text = "\n" + text

                expr = self.repl_parser.parse(text)

                if expr is not None:
                    print(expr.evaluate(self.environment))
                    cont = False
                else:
                    cont = True

            except Exception as e:
                if cont:
                    cont = False
                print(f"{e.__class__.__qualname__}: {e}")
