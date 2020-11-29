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
      environment (:class:`.environment.Environment`): An
        :class:`.environment.Environment` instance containing the
        built-in functions and a reference to the
        :class:`.engine.Engine` instance wrapped within a
        :class:`.amalgams.Internal`, accessible through the
        `~engine~` key.
    """

    def __init__(self) -> None:
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
        buffer = []
        session:  PromptSession = PromptSession()

        while True:
            line = session.prompt(prompt if not cont else prompt_cont)

            buffer.append(line)

            lines = "\n".join(buffer)

            try:
                expr = pr.parse(lines)
                result = expr.evaluate(self.environment)

            except pr.MissingClosing:
                cont = True

            except EOFError:
                pd._exit(self.environment)

            except am.FailureStack as s:
                print(s.make_report(lines, "<stdin>"), file=sys.stderr)
                buffer.clear()
                cont = False

            except Exception as e:
                buffer.clear()
                cont = False
                print(f"{e.__class__.__qualname__}: {e}")

            else:
                print(result)
                buffer.clear()
                cont = False

    def _interpret(self, text: str, source: str = "<unknown>") -> am.Amalgam:
        """
        Parses and runs a :data:`text` from a :data:`source`.

        Internal-facing method intended for use within
        :mod:`amalgam.primordials`.
        """
        return pr.parse(text, source).evaluate(self.environment)

    def interpret(
        self, text: str, source: str = "<unknown>", file: IO = sys.stdout
    ) -> None:
        """
        Parses and runs a :data:`text` from a :data:`source`.

        User-facing method intended for use within :mod:`amalgam.cli`.
        Prints the result to :data:`sys.stdout` unless specified.
        Handles pretty-printing of :class:`.amalgams.Notifications`.
        """
        try:
            result = self._interpret(text, source)
        except am.FailureStack as s:
            print(s.make_report(text, source), file=sys.stderr)
        else:
            print(result, file=file)
