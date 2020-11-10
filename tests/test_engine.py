import re

from amalgam.amalgams import Numeric, String
from amalgam.engine import Engine

from pytest import fixture, raises


@fixture
def mock_prompt(mocker):
    MockClassPromptSession = mocker.Mock()
    MockSelfPromptSession = mocker.Mock()

    MockClassPromptSession.return_value = MockSelfPromptSession

    mocker.patch("amalgam.engine.PromptSession", MockClassPromptSession)

    return MockSelfPromptSession.prompt


def test_engine_repl(mock_prompt, capsys):
    mock_prompt.side_effect = (
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

        "(+ x)",

        "(exit 0)",
    )

    with raises(SystemExit):
        Engine().repl()

    out, err = capsys.readouterr()

    assert out == (
        "84\n"
        "6\n"
        "[1 2 3 4]\n"
        "[4 3 2 1]\n"
        "ZeroDivisionError: division by zero\n"
        "ZeroDivisionError: division by zero\n"
        "Goodbye.\n"
    )

    assert err != ""



def test_engine_repl_eof(mock_prompt, capsys):
    mock_prompt.side_effect = EOFError

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

    assert capsys.readouterr().err != ""
