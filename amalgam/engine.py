from prompt_toolkit import PromptSession

from amalgam.amalgams import Amalgam, Environment
from amalgam.primordials import FUNCTIONS, _exit
from amalgam.parser import Parser


class Engine:

    def __init__(
        self, *, prompt: str = "> ", prompt_cont: str = "| ",
    ) -> None:

        self.prompt = prompt
        self.prompt_cont = prompt_cont

        self.parser = Parser()
        self.environment = Environment(
            {**FUNCTIONS, "~engine~": self}
        )

    def repl(self) -> None:
        cont = False
        session = PromptSession()

        while True:
            try:
                prompt = self.prompt if not cont else self.prompt_cont

                text = session.prompt(prompt)

                if cont:
                    text = "\n" + text

                expr = self.parser.repl_parse(text)

                if expr is not None:
                    print(expr.evaluate(self.environment))
                    cont = False
                else:
                    cont = True

            except EOFError:
                _exit(self.environment)

            except Exception as e:
                if cont:
                    cont = False
                print(f"{e.__class__.__qualname__}: {e}")

    def parse_and_run(self, text: str) -> Amalgam:
        return self.parser.parse(text).evaluate(self.environment)
