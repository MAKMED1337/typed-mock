from collections.abc import Callable

import pytest

from typed_mock import FOREVER, FieldAccessedError, Mocker, ValidationConfig


def ff() -> int:
    return 5


class F:
    """F class"""

    g = 43
    lam: Callable[..., int] = lambda: 5
    func = ff

    def f(self) -> int:
        return 3

    @staticmethod
    def st(x: int) -> int:
        return 4 + x

    @classmethod
    def cl(cls, x: int) -> int:
        return cls.g + x

    def mult(self, *_: object, **__: object) -> None:
        return None


def test_mocking_nonfunction() -> None:
    mocker = Mocker()
    f = mocker.mock(F)

    _ = f.st
    _ = f.cl
    _ = f.lam
    _ = f.func  # type: ignore[misc]
    with pytest.raises(FieldAccessedError):
        _ = f.g

    mocker = Mocker(ValidationConfig(raise_on_field_access=False))
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


def test_wraps_class() -> None:
    mocker = Mocker()
    f = mocker.mock(F)
    assert isinstance(f, F)
    # Unfortunately I have no idea how to fake type(f) is F

    mocker = Mocker(ValidationConfig(raise_on_field_access=False))
    f = mocker.mock(F)
    assert f.__doc__ == 'F class'


def test_effect_mocks_only() -> None:
    mocker = Mocker()

    f = mocker.mock(F)
    mocker.when(f.f).return_(1, times=FOREVER)
    assert f.f() == 1

    g = F()
    assert g.f() == 3


def test_mock_static() -> None:
    mocker = Mocker()

    def qq() -> int:
        """ds"""
        return 3

    mocker.when(qq).return_(4, times=FOREVER)

    assert qq() == 4
    with pytest.raises(TypeError):
        assert qq(43) == 4  # type: ignore[call-arg]

    assert qq.__doc__ == 'ds'
    assert qq.__name__ == 'qq'
