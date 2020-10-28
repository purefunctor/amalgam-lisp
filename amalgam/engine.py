from prompt_toolkit import PromptSession

import amalgam.amalgams as am
import amalgam.environment as ev
import amalgam.primordials as pd
import amalgam.parser as pr


class Engine:
    """
    Class that serves as the frontend for parsing and running programs.
    """

    def __init__(self) -> None:
        self.parser = pr.Parser()
        self.environment = ev.Environment(
            {**pd.FUNCTIONS, "~engine~": am.Internal(self)}
        )

    def repl(self, *, prompt: str = "> ", prompt_cont: str = "| ") -> None:
        """Runs a REPL session that supports multi-line input."""
        cont = False
        session = PromptSession()

        while True:
            try:
                text = session.prompt(prompt if not cont else prompt_cont)

                if cont:
                    text = "\n" + text

                expr = self.parser.repl_parse(text)

                if expr is not None:
                    print(expr.evaluate(self.environment))
                    cont = False
                else:
                    cont = True

            except EOFError:
                pd._exit(self.environment)

            except Exception as e:
                if cont:
                    cont = False
                print(f"{e.__class__.__qualname__}: {e}")

    def parse_and_run(self, text: str) -> am.Amalgam:
        """Parses and runs the given `text` string."""
        return self.parser.parse(text).evaluate(self.environment)
