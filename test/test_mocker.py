from collections.abc import Callable
from typing import Any

import pytest

from typed_mock import AttributeAccessedError, Mocker
from typed_mock.common import ValidationConfig


def ff() -> int:
    return 5


class F:
    g = 43
    lam: Callable[..., Any] = lambda: 5
    func = ff

    def f(self) -> int:
        return 3

    @staticmethod
    def st(x: int) -> int:
        return 4 + x

    @classmethod
    def cl(cls, x: int) -> int:
        return cls.g + x


def test_mocking_nonfunction() -> None:
    mocker = Mocker()
    f = mocker.mock(F)

    _ = f.st
    _ = f.cl
    _ = f.lam
    _ = f.func  # type: ignore[misc]
    with pytest.raises(AttributeAccessedError):
        _ = f.g

    mocker = Mocker(ValidationConfig(raise_on_attribute=False))
    f = mocker.mock(F)
    _ = f.g
    _ = f.lam
    _ = f.func  # type: ignore[misc]


def test_nonexistent_method() -> None:
    mocker = Mocker()

    f = mocker.mock(F)

    with pytest.raises(AttributeError):
        mocker.when(f.k).return_(5)  # type: ignore[attr-defined]
