import sys
from typing import IO

from prompt_toolkit import PromptSession

import amalgam.amalgams as am
import amalgam.environment as ev
import amalgam.primordials as pd
import amalgam.parser as pr


class Engine:
    """
    Class that serves as the frontend for parsing and running programs.

    Attributes:
      parser (:class:`.parser.Parser`): A :class:`.parser.Parser`
        instance.

      environment (:class:`.environment.Environment`): An
        :class:`.environment.Environment` instance containing the
        built-in functions and a reference to the
        :class:`.engine.Engine` instance wrapped within a
        :class:`.amalgams.Internal`, accessible through the
        `~engine~` key.
    """

    def __init__(self) -> None:
        self.parser = pr.Parser()
        self.environment = ev.Environment(
            bindings={**pd.FUNCTIONS}, name="global", engine=self,
        )

    def repl(self, *, prompt: str = "> ", prompt_cont: str = "| ") -> None:
        """
        Runs a REPL session that supports multi-line input.

        Parameters:
          prompt (:class:`str`): The style of the prompt on
            regular lines.

          prompt_cont (:class:`str`): The style of the prompt on
            continued lines.
        """
        cont = False
        session: PromptSession = PromptSession()

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

    def _interpret(self, text: str, source: str = "<unknown>") -> am.Amalgam:
        """
        Parses and runs a :data:`text` from a :data:`source`.

        Internal-facing method intended for use within
        :mod:`amalgam.primordials`.
        """
        return self.parser.parse(text, source).evaluate(self.environment)

    def interpret(
        self, text: str, source: str = "<unknown>", file: IO = sys.stdout
    ) -> None:
        """
        Parses and runs a :data:`text` from a :data:`source`.

        User-facing method intended for use within :mod:`amalgam.cli`.
        Prints the result to :data:`sys.stdout` unless specified.
        Handles pretty-printing of :class:`.amalgams.Notifications`.
        """
        result = self._interpret(text, source)
        if isinstance(result, am.Notification):
            print(result, file=sys.stderr)
        else:
            print(result, file=file)
