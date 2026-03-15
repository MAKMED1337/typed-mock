import pytest

from typed_mock import FOREVER, FieldAccessedError, Mocker, ValidationConfig, ValueIsNotSetError
from typed_mock.errors import InvalidCallableError

from .common import F


def test_mocking_nonfunction() -> None:
    mocker = Mocker()
    f = mocker.mock(F)

    _ = f.st
    _ = f.cl
    with pytest.raises(InvalidCallableError):
        _ = f.lam
    with pytest.raises(InvalidCallableError):
        _ = f.func  # type: ignore[misc]
    with pytest.raises(FieldAccessedError):
        _ = f.val

    mocker = Mocker(ValidationConfig(raise_on_field_access=False))
    f = mocker.mock(F)

    _ = f.val
    with pytest.raises(InvalidCallableError):
        _ = f.lam
    with pytest.raises(InvalidCallableError):
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


def test_unset_function() -> None:
    mocker = Mocker()

    f = mocker.mock(F)
    with pytest.raises(ValueIsNotSetError):
        f.f()
