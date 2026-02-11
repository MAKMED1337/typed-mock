from collections.abc import Callable
from typing import Any

import pytest

from typed_mock import AttributeAccessedError, Mocker, ValidationConfig
from typed_mock.common import FOREVER


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

    def mult(self, *args: object, **kwargs: object) -> None:
        return None


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


def test_invalid_arguments() -> None:
    mocker = Mocker()

    f = mocker.mock(F)
    with pytest.raises(TypeError):
        f.f(34)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        f.st()  # type: ignore[call-arg]

    mocker.when(f.mult).return_(None, times=FOREVER)
    f.mult()
    f.mult(1314, 234, x=1234)

    mocker = Mocker(ValidationConfig(validate_call_arguments=False))
    f = mocker.mock(F)

    mocker.when(f.f).return_(33)
    f.f(34)  # type: ignore[call-arg]
