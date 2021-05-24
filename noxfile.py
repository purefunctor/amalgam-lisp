import tempfile

import nox


def install_with_constraints(session, *args, **kwargs):
    """
    https://cjolowicz.github.io/posts/hypermodern-python-03-linting/
    """
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            f"--output={requirements.name}",
            "--without-hashes",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)


@nox.session
def docs(session):
    install_with_constraints(session, "sphinx", "sphinx_rtd_theme")
    session.install(".")
    session.run("sphinx-build", "docs", "docs/build")


@nox.session
def lint(session):
    install_with_constraints(session, "pre-commit")
    session.run("pre-commit", "install")
    session.run("pre-commit", "run", "--all-files")


@nox.session(python=("3.7", "3.8", "3.9"))
def test(session):
    env = {"COVERAGE_FILE": f".coverage.{session.python}"}

    install_with_constraints(session, "pytest", "pytest-mock", "coverage")
    session.install(".")
    session.run("coverage", "run", "--branch", "-m", "pytest", "-vs", env=env)
    session.run("coverage", "report", "-m", env=env)


@nox.session(name="test-pypy-3.7", python=("pypy3.7"))
def test_pypy(session):
    env = {"COVERAGE_FILE": f".coverage.{session.python}"}

    install_with_constraints(session, "pytest", "pytest-mock", "coverage")
    session.install(".")
    session.run("coverage", "run", "--branch", "-m", "pytest", "-vs", env=env)
    session.run("coverage", "report", "-m", env=env)


@nox.session
def coverage(session):
    install_with_constraints(session, "coverage[toml]")
    session.run("coverage", "combine")
    session.run("coverage", "report", "-m")
    session.run("coverage", "html")
