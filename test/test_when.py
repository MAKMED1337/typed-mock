import pytest

from typed_mock import (
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
    when(f.f).return_once(3)
    assert f.f() == 3
    with pytest.raises(ValueIsNotSetError):
        assert f.f() == 3

    when(f.f).return_once(4)
    assert f.f() == 4


def test_return_forever() -> None:
    f = mock(F)
    when(f.f).return_forever(2)

    for _ in range(10):
        assert f.f() == 2


def test_invalid_method() -> None:
    f = mock(F)

    with pytest.raises(FunctionNotFoundError):
        when(f.g).return_once(5)  # type: ignore[attr-defined]

    f = mock(F, strict=False)
    when(f.g).return_once(6)  # type: ignore[attr-defined]


def test_stacking() -> None:
    f = mock(F)

    when(f.f).return_once(6)
    when(f.f).return_once(7)
    when(f.f).return_forever(8)

    assert f.f() == 6
    assert f.f() == 7
    for _ in range(10):
        assert f.f() == 8


def test_raise_once() -> None:
    f = mock(F)

    when(f.f).raise_once(FError)
    when(f.f).return_once(1)
    when(f.f).raise_once(FError)

    with pytest.raises(FError):
        f.f()

    assert f.f() == 1

    with pytest.raises(FError):
        f.f()


def test_raise_forever() -> None:
    f = mock(F)

    when(f.f).return_once(1)
    when(f.f).raise_forever(FError)

    assert f.f() == 1

    for _ in range(10):
        with pytest.raises(FError):
            f.f()
