from amalgam.cli import amalgam_main

from click.testing import CliRunner


def test_invoke_repl(mocker):
    MockClassEngine = mocker.Mock()
    MockSelfEngine = mocker.Mock()

    MockClassEngine.return_value = MockSelfEngine

    mocker.patch("amalgam.cli.Engine", MockClassEngine)

    CliRunner().invoke(amalgam_main)

    MockClassEngine.assert_called_once()
    MockSelfEngine.repl.assert_called_once()


def test_invoke_expr():
    result = CliRunner().invoke(amalgam_main, ["--expr", "(+ 42 42)"])
    assert result.exit_code == 0
    assert result.stdout == "84\n"


def test_invoke_file():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("plus.al", "w") as f:
            f.write("(print (+ 42 42))")

        result = runner.invoke(amalgam_main, ["plus.al"])

        assert result.exit_code == 0
        assert result.stdout == "84\n"


def test_invoke_file_expr_mix_fail():
    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("plus.al", "w") as f:
            f.write("(+ 42 42)")

            result = runner.invoke(amalgam_main, ["plus.al", "--expr", "(+ 42 42)"])

            assert result.exit_code == 2
            assert result.stdout == (
                "Usage: amalgam-main [OPTIONS] [FILE]\n\n"
                "Error: Invalid value: Cannot use FILE and --expr together\n"
            )
