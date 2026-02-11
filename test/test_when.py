import pytest

from typed_mock import (
    FOREVER,
    FunctionNotFoundError,
    ValueIsNotSetError,
    mock,
    when,
)


class F:
    def f(self) -> int:
        return 3


class FError(Exception):
    pass


def test_return_once() -> None:
    f = mock(F)
    when(f.f).return_(3)
    assert f.f() == 3
    with pytest.raises(ValueIsNotSetError):
        assert f.f() == 3

    when(f.f).return_(4)
    assert f.f() == 4

    with pytest.raises(ValueError, match='Times'):
        when(f.f).return_(4, times=0)

    with pytest.raises(ValueError, match='Times'):
        when(f.f).return_(4, times=-2)


def test_return_forever() -> None:
    f = mock(F)
    when(f.f).return_(2, times=FOREVER)

    for _ in range(10):
        assert f.f() == 2


def test_invalid_method() -> None:
    f = mock(F)

    with pytest.raises(FunctionNotFoundError):
        when(f.g).return_(5)  # type: ignore[attr-defined]

    f = mock(F, strict=False)
    when(f.g).return_(6)  # type: ignore[attr-defined]


def test_stacking() -> None:
    f = mock(F)

    when(f.f).return_(6)
    when(f.f).return_(7)
    when(f.f).return_(8, times=FOREVER)

    assert f.f() == 6
    assert f.f() == 7
    for _ in range(10):
        assert f.f() == 8


def test_return_multiple() -> None:
    f = mock(F)

    when(f.f).return_(1, 2, 3)
    assert f.f() == 1
    assert f.f() == 2
    assert f.f() == 3

    with pytest.raises(ValueIsNotSetError):
        assert f.f() == 4

    with pytest.raises(ValueError, match='value'):
        when(f.f).return_(1, 2, times=3)


def test_raise_once() -> None:
    f = mock(F)

    when(f.f).raise_(FError)
    when(f.f).return_(1)
    when(f.f).raise_(FError)

    with pytest.raises(FError):
        f.f()

    assert f.f() == 1

    with pytest.raises(FError):
        f.f()


def test_raise_forever() -> None:
    f = mock(F)

    when(f.f).return_(1)
    when(f.f).raise_(FError, times=FOREVER)

    assert f.f() == 1

    for _ in range(10):
        with pytest.raises(FError):
            f.f()
