import pytest

from typed_mock import (
    FOREVER,
    Args,
    CalledWithWrongValueError,
    InvalidArgumentsToCalledWithError,
    Mocker,
    ValueIsNotSetError,
)


class F:
    def f(self) -> int:
        return 3

    def g(self, x: int, y: int) -> int:
        return x + y


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

    with pytest.raises(ValueError, match='times'):
        mocker.when(f.f).return_(1, 2, times=3)  # type: ignore[call-overload]


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


def test_called_with_partial() -> None:
    mocker = Mocker()
    f = mocker.mock(F)

    mocker.when(f.f).called_with_partial(return_=33)
    assert f.f() == 33

    mocker.when(f.g).called_with_partial(return_=33)
    assert f.g(1, 2) == 33

    mocker.when(f.g).called_with_partial(1, return_=33)
    assert f.g(1, 2) == 33

    mocker.when(f.g).called_with_partial(x=1, return_=33)
    assert f.g(1, 2) == 33

    mocker.when(f.g).called_with_partial(y=2, return_=33)
    assert f.g(1, 2) == 33

    mocker.when(f.g).called_with_partial(1, y=2, return_=33)
    assert f.g(1, 2) == 33

    mocker.when(f.g).called_with_partial(-1, return_=33)
    with pytest.raises(CalledWithWrongValueError):
        f.g(1, 2)

    mocker.when(f.g).called_with_partial(x=-1, return_=33)
    with pytest.raises(CalledWithWrongValueError):
        f.g(1, 2)

    mocker.when(f.g).called_with_partial(y=-2, return_=33)
    with pytest.raises(CalledWithWrongValueError):
        f.g(1, 2)

    with pytest.raises(InvalidArgumentsToCalledWithError):
        mocker.when(f.f).called_with_partial(33, return_=43)

    with pytest.raises(InvalidArgumentsToCalledWithError):
        mocker.when(f.f).called_with_partial(x=1234, return_=43)


def test_called_with_full() -> None:
    mocker = Mocker()
    f = mocker.mock(F)

    mocker.when(f.f).called_with_full(Args(), 33)
    assert f.f() == 33

    mocker.when(f.g).called_with_full(Args(1, 2), 33)
    assert f.g(1, 2) == 33

    mocker.when(f.g).called_with_full(Args(1, y=2), 33)
    assert f.g(1, 2) == 33

    mocker.when(f.g).called_with_full(Args(x=1, y=2), 33)
    assert f.g(1, 2) == 33

    mocker.when(f.g).called_with_full(Args(-1, 2), 33)
    with pytest.raises(CalledWithWrongValueError):
        f.g(1, 2)

    with pytest.raises(InvalidArgumentsToCalledWithError):
        mocker.when(f.g).called_with_full(Args(), 33)  # type: ignore[call-arg]

    with pytest.raises(InvalidArgumentsToCalledWithError):
        mocker.when(f.g).called_with_full(Args(1), 33)  # type: ignore[call-arg]

    with pytest.raises(InvalidArgumentsToCalledWithError):
        mocker.when(f.g).called_with_full(Args(x=1), 33)  # type: ignore[call-arg]

    with pytest.raises(InvalidArgumentsToCalledWithError):
        mocker.when(f.g).called_with_full(Args(y=2), 33)  # type: ignore[call-arg]

    with pytest.raises(InvalidArgumentsToCalledWithError):
        mocker.when(f.f).called_with_full(Args(33), 43)  # type: ignore[call-arg]
