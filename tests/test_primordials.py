from amalgam.amalgams import Numeric
from amalgam.primordials import (
    _add,
    _sub,
    _mul,
    _div,
    _setn,
    _fn,
    _mkfn,
)

from pytest import mark, param

from tests.utils import (
    MockEnvironment,
    MockFunction,
    MockNumeric,
    MockQuoted,
    MockSExpression,
    MockSymbol,
    MockVector,
)


arithmetics = (
    param(
        arith_fn,
        arith_nm,
        arith_rs,
        id=f"({arith_op} {' '.join(map(str, arith_nm))})"
    )
    for arith_fn, arith_op, arith_nm, arith_rs in (
        (_add, "+", (1, 2), 1 + 2),
        (_add, "+", (1, 2, 3), 1 + 2 + 3),
        (_sub, "-", (5, 3), 5 - 3),
        (_sub, "-", (3, 5, 3), 3 - (5 + 3)),
        (_mul, "*", (2, 2), 2 * 2),
        (_mul, "*", (2, 2, 2), 2 * 2 * 2),
        (_div, "/", (4, 2), 4 / 2),
        (_div, "/", (6, 2, 3), 6 / (2 * 3)),
    )
)


@mark.parametrize(("arith_fn", "arith_nm", "arith_rs"), arithmetics)
def test_arithmetic_function(arith_fn, arith_nm, arith_rs):
    assert arith_fn(MockEnvironment(), *map(Numeric, arith_nm)).value == arith_rs


def test_setn():
    mock_env = MockEnvironment()
    mock_name = MockQuoted(MockSymbol("setn-test"))
    mock_amalgam = MockQuoted(MockNumeric(42))
    mock_env.iget.return_value = mock_amalgam

    _setn_result = _setn(mock_env, mock_name, mock_amalgam)

    mock_env.iset.assert_called_once_with(mock_name.value.value, mock_amalgam.value)
    mock_env.iget.assert_called_once_with(mock_name.value.value)
    assert _setn_result == mock_amalgam


def test_fn(mocker):
    mock_env = MockEnvironment()
    mock_args = MockQuoted(MockVector(MockSymbol("x")))
    mock_body = MockQuoted(MockSymbol("x"))
    mock_create_fn = mocker.Mock(return_value=MockFunction("~lambda~"))

    mocker.patch("amalgam.primordials.create_fn", mock_create_fn)

    _fn_result = _fn(mock_env, mock_args, mock_body)

    mock_create_fn.assert_called_once_with(
        "~lambda~",
        [mock_arg.value for mock_arg in mock_args.value.vals],
        mock_body.value,
    )
    assert _fn_result == mock_create_fn.return_value


def test_mkfn(mocker):
    mock_env = MockEnvironment()
    mock_name = MockQuoted(MockSymbol("mkfn-test"))
    mock_args = MockQuoted(MockVector(MockSymbol("x")))
    mock_body = MockQuoted(MockSymbol("x"))
    mock_Function = MockFunction()
    mock_Function.with_name.return_value = mock_Function
    mock_fn = mocker.Mock(return_value=mock_Function)
    mock_setn = mocker.Mock(return_value=mock_Function)

    mocker.patch("amalgam.primordials._fn", mock_fn)
    mocker.patch("amalgam.primordials._setn", mock_setn)

    _mkfn_result = _mkfn(mock_env, mock_name, mock_args, mock_body)

    mock_fn.assert_called_once_with(mock_env, mock_args, mock_body)
    mock_Function.with_name.assert_called_once_with(mock_name.value.value)
    mock_setn.assert_called_once_with(mock_env, mock_name, mock_Function)
    assert _mkfn_result == mock_Function
