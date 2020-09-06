from fractions import Fraction
import re
from typing import Any

from amalgam.amalgams import (
    create_fn,
    Amalgam,
    Deferred,
    Environment,
    Function,
    Numeric,
    SExpression,
    String,
    Symbol,
    Vector,
)

from pytest import fixture


@fixture
def numerics():
    return Numeric(21), Numeric(21.42), Numeric(Fraction(21, 42))


def test_numeric_evaluate(numerics):
    for numeric in numerics:
        assert numeric == numeric.evaluate(Environment())


@fixture
def strings():
    return String(""), String("\n\t"), String("foo-bar-baz")


def test_string_evaluate(strings):
    for string in strings:
        assert string == string.evaluate(Environment())


def test_symbol_evaluate():
    symbol = Symbol("foo")
    environ = Environment(None, {"foo": String("bar")})
    assert symbol.evaluate(environ) == environ["foo"]


@fixture
def num():
    return Numeric(42)


@fixture
def env():
    return Environment()


def test_s_expression_evaluate_simple(num, env):
    """
    Simple test for SExpression

    Aside from testing basic usage of SExpression, this test also
    showcases how simple builtin functions are to be implemented.
    """

    # Define the variadic plus function
    def plus_func(_environment: Environment, *numbers: Numeric) -> Numeric:
        return Numeric(sum(number.value for number in numbers))

    # Inject it to the environment
    env["+"] = Function("+", plus_func)

    # Build the S-Expression: (+ 42 42)
    s_expression = SExpression(Symbol("+"), num, num)

    # Evaluate the S-Expression given the Environment
    assert s_expression.evaluate(env).value == num.value + num.value


def test_s_expression_evaluate_macro(num, env):
    """
    Macro test for SExpression

    This test details how a macro such as `fn` for defining lambdas
    can be defined within Python, as well as testing the cascading
    `evaluate` functionality of SExpression.
    """

    # Define the variadic plus function
    def plus_func(_environment: Environment, *numbers: Numeric) -> Numeric:
        return Numeric(sum(number.value for number in numbers))

    # Inject it to the environment
    env["+"] = Function("+", plus_func)

    # Define the fn macro for defining lambdas
    def fn_func(
        _env: Environment, args: Deferred[Vector[Symbol]], body: Deferred[Amalgam],
    ) -> Function:
        return create_fn("<lambda>", [arg.value for arg in args.value.vals], body.value)

    # Inject it to the environment
    env["fn"] = Function("fn", fn_func)

    # Inject a global Numeric
    env["z"] = num

    # Build the S-Expression: ((fn (x y) (+ x y z)) 42 42)
    expr = SExpression(
        SExpression(
            Symbol("fn"),
            Deferred(
                Vector(Symbol("x"), Symbol("y"))
            ),
            Deferred(
                SExpression(Symbol("+"), Symbol("x"), Symbol("y"), Symbol("z"))
            ),
        ),
        num,
        num,
    )

    # Evaluate the S-Expression given the Environment
    expr.evaluate(env) == Numeric(num.value + num.value + num.value)


def test_s_expression_evaluate_binding(num, env):
    """
    Binding test for SExpression

    This test showcases the ability of SExpression and Function to
    create and remember closures.
    """

    # Define the variadic plus function
    def plus_func(_environment: Environment, *numbers: Numeric) -> Numeric:
        return Numeric(sum(number.value for number in numbers))

    # Inject it to the environment
    env["+"] = Function("+", plus_func)

    # Define the fn macro for defining lambdas
    def fn_func(
        _env: Environment, args: Deferred[Vector[Symbol]], body: Deferred[Amalgam],
    ) -> Function:
        return create_fn("<lambda>", [arg.value for arg in args.value.vals], body.value)

    # Inject it to the environment
    env["fn"] = Function("fn", fn_func)

    # Inject a global Numeric
    env["z"] = num

    # Build the S-Expression: (((fn (x) (fn (y) (+ x y z))) 42) 42)
    expr = SExpression(
        SExpression(
            SExpression(
                Symbol("fn"),
                Deferred(
                    Vector(Symbol("x"))
                ),
                Deferred(
                    SExpression(
                        Symbol("fn"),
                        Deferred(
                            Vector(Symbol("y"))
                        ),
                        Deferred(
                            SExpression(
                                Symbol("+"),
                                Symbol("x"),
                                Symbol("y"),
                                Symbol("z"),
                            )
                        ),
                    )
                ),
            ),
            num,
        ),
        num
    )

    # Evaluate the S-Expression given the Environment
    assert expr.evaluate(env) == Numeric(num.value + num.value + num.value)


def test_s_expression_evaluate_infect(num, env):
    """
    Injection test for SExpression

    This test showcases the ability of SExpression and Function to
    inject values into the environment.
    """

    # Define the variadic plus function
    def plus_func(_environment: Environment, *numbers: Numeric) -> Numeric:
        return Numeric(sum(number.value for number in numbers))

    # Inject it to the environment
    env["+"] = Function("+", plus_func)

    # Define the fn macro for defining lambdas
    def fn_func(
        _env: Environment, args: Deferred[Vector[Symbol]], body: Deferred[Amalgam],
    ) -> Function:
        return create_fn("<lambda>", [arg.value for arg in args.value.vals], body.value)

    # Inject it to the environment
    env["fn"] = Function("fn", fn_func)

    # Define the defun macro for defining functions
    def defun_func(
        env: Environment, name: Deferred[String], args: Deferred[Vector[Symbol]], body: Deferred[Amalgam]
    ) -> Function:
        env[name.value.value] = fn_func(env, args, body)
        return env[name.value.value]

    # Inject it to the environment
    env["defun"] = Function("defun", defun_func)

    # Define the prog macro for defining a program
    def prog_func(env: Environment, *expressions: Deferred[SExpression]) -> Vector[Amalgam]:
        return Vector(*(expression.evaluate(env) for expression in expressions))

    # Inject it to the environment
    env["prog"] = Function("prog", prog_func)

    # Build the S-Expression: (prog (defun my-plus (x y) (+ x y)) (my-plus 42 42))
    expr = SExpression(
        Symbol("prog"),
        SExpression(
            Symbol("defun"),
            Deferred(String("my-plus")),
            Deferred(Vector(Symbol("x"), Symbol("y"))),
            Deferred(SExpression(Symbol("+"), Symbol("x"), Symbol("y"))),
        ),
        SExpression(
            Symbol("my-plus"), num, num,
        ),
    )

    assert expr.evaluate(env).vals[1] == Numeric(num.value + num.value)


def test_vector_evaluate_literals(numerics, env):
    vector = Vector(*numerics)
    assert vector.evaluate(env) == vector


def test_vector_evaluate_symbols(numerics, env):
    vector = Vector(*map(Symbol, "xyz"))
    for name, numeric in zip("xyz", numerics):
        env[name] = numeric
    assert vector.evaluate(env) == Vector(*numerics)


def test_deferred_evaluate(num, env):
    deferred = Deferred(num)
    assert deferred.evaluate(env) == deferred


def test_function_binding(num, env):
    fnc = create_fn("binding-test", "_x", num)
    assert fnc.bind(env).env == env


def test_function_evalulate(num, env):
    fnc = create_fn("evaluate-test", "_x", num)
    assert fnc.evaluate(env) == fnc


def test_function_evaluate_literal(num, env):
    fnc = create_fn("literal-test", "_x", num)
    assert fnc.call(env, num).value == num.value


def test_function_evaluate_symbol_global(num, env):
    env["x"] = num
    fnc = create_fn("global-test", "", Symbol("x"))
    assert fnc.call(env).value == num.value


def test_function_evaluate_symbol_local(num, env):
    env["x"] = String("fail")
    fnc = create_fn("local-test", "x", Symbol("x"))
    assert fnc.call(env, num).value == num.value


def test_function_evaluate_symbol_closure(num, env):
    fnc = create_fn("closure-test", "x", create_fn("inner", "y", Symbol("x")))
    assert fnc.call(env, num).call(env, num).value == num.value
