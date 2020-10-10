from dataclasses import fields
from enum import Enum
from functools import partial
from typing import Sequence

import amalgam.amalgams as am
import unittest.mock as mk


class AmalgamMockMixin:
    """
    Mixin for creating a custom `Mock` for an `Amalgam`.

    Modifies `Mock._get_child_mock` to return a `MagicMock`
    instance instead of the parent class. Also frees the
    `name` keyword from being tightly bound as a parameter
    for `Mock`, and allows it to be used by the subclasses
    instead. As such, `__mock_name` can be used to set the
    name of the `Mock`.
    """

    spec_set = None

    def __init__(self, **keywords):
        mock_name = keywords.pop("__mock_name", "mock")

        super().__init__(spec_set=self.spec_set, name=mock_name, **keywords)

    def _get_child_mock(self, **keywords):
        return mk.MagicMock(**keywords)


class MockEnvironment(AmalgamMockMixin, mk.MagicMock):
    """Mocks an `Environment`."""
    spec_set = am.Environment(mk.MagicMock(), mk.MagicMock())


class MockAmalgam(AmalgamMockMixin, mk.MagicMock):
    """
    Mocks a generalized `Amalgam` object.

    The `value` and `vals` attributes are mocked and can be set
    through the `value` and `vals` keyword arguments respectively.

    The return values for the `evaluate` and `call` methods are also
    mocked and can be set with the `evaluate` and `call` keyword
    arguments, while the return value for the `bind` method is the
    `MockAmalgam` instance.
    """

    spec_set = ("value", "vals", "evaluate", "bind", "call")

    def __init__(
        self,
        *,
        value=None,
        vals=None,
        evaluate=None,
        call=None,
        **keywords,
    ):
        super().__init__(**keywords)

        self.value = value if value is not None else mk.MagicMock()
        self.vals = tuple(vals) if isinstance(vals, Sequence) else mk.MagicMock()

        self.evaluate.return_value = evaluate if evaluate is not None else self
        self.bind.return_value = self

        if call is None:
            self.call.side_effect = NotImplementedError
        else:
            self.call.return_value = call
