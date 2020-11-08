import re

from amalgam.amalgams import Numeric, String
from amalgam.engine import Engine

from pytest import raises


def test_engine_repl(mocker, capsys):
    MockClassPromptSession = mocker.Mock()
    MockSelfPromptSession = mocker.Mock()

    MockClassPromptSession.return_value = MockSelfPromptSession
    MockSelfPromptSession.prompt.side_effect = (
        "(+ 42 42)",

        "(+ 1",
        "2 3)",

        "[1 2 3 4]",

        "[4 3",
        "2 1]",

        "(/ 1 0)",

        "(/",
        " 1",
        " 0",
        ")",

        "(exit 0)",
    )

    mocker.patch("amalgam.engine.PromptSession", MockClassPromptSession)

    with raises(SystemExit):
        Engine().repl()

    assert capsys.readouterr().out == (
        "84\n"
        "6\n"
        "[1 2 3 4]\n"
        "[4 3 2 1]\n"
        "ZeroDivisionError: division by zero\n"
        "ZeroDivisionError: division by zero\n"
        "Goodbye.\n"
    )

    MockSelfPromptSession.prompt.side_effect = EOFError

    with raises(SystemExit):
        Engine().repl()

    assert capsys.readouterr().out == "Goodbye.\n"


def test_engine_internal_interpret():
    engine = Engine()

    assert engine._interpret("(setn x 21)") == Numeric(21)
    assert engine._interpret("(+ x x x x)") == Numeric(84)


def test_engine_external_interpret(capsys):
    engine = Engine()

    numeric = engine._interpret("(+ 21 21)")
    engine.interpret("(print (+ 21 21))")

    assert capsys.readouterr().out == "42\n"

    engine.interpret("(+ x x)")

    assert re.match("<Notification .+?>", capsys.readouterr().err)
