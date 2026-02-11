import pytest

from typed_mock import (
    FOREVER,
    Mocker,
    ValueIsNotSetError,
)


class F:
    def f(self) -> int:
        return 3


class FError(Exception):
    pass


def test_return_once() -> None:
    mocker = Mocker()
    f = mocker.mock(F)
    mocker.when(f.f).return_(3)
    assert f.f() == 3
    with pytest.raises(ValueIsNotSetError):
        assert f.f() == 3

    mocker.when(f.f).return_(4)
    assert f.f() == 4

    with pytest.raises(ValueError, match='Times'):
        mocker.when(f.f).return_(4, times=0)

    with pytest.raises(ValueError, match='Times'):
        mocker.when(f.f).return_(4, times=-2)


def test_return_forever() -> None:
    mocker = Mocker()

    f = mocker.mock(F)
    mocker.when(f.f).return_(2, times=FOREVER)

    for _ in range(10):
        assert f.f() == 2


def test_stacking() -> None:
    mocker = Mocker()

    f = mocker.mock(F)

    mocker.when(f.f).return_(6)
    mocker.when(f.f).return_(7)
    mocker.when(f.f).return_(8, times=FOREVER)

    assert f.f() == 6
    assert f.f() == 7
    for _ in range(10):
        assert f.f() == 8


def test_return_multiple() -> None:
    mocker = Mocker()
    f = mocker.mock(F)

    mocker.when(f.f).return_(1, 2, 3)
    assert f.f() == 1
    assert f.f() == 2
    assert f.f() == 3

    with pytest.raises(ValueIsNotSetError):
        assert f.f() == 4

    with pytest.raises(ValueError, match='value'):
        mocker.when(f.f).return_(1, 2, times=3)


def test_raise_once() -> None:
    mocker = Mocker()
    f = mocker.mock(F)

    mocker.when(f.f).raise_(FError)
    mocker.when(f.f).return_(1)
    mocker.when(f.f).raise_(FError)

    with pytest.raises(FError):
        f.f()

    assert f.f() == 1

    with pytest.raises(FError):
        f.f()


def test_raise_forever() -> None:
    mocker = Mocker()
    f = mocker.mock(F)

    mocker.when(f.f).return_(1)
    mocker.when(f.f).raise_(FError, times=FOREVER)

    assert f.f() == 1

    for _ in range(10):
        with pytest.raises(FError):
            f.f()
