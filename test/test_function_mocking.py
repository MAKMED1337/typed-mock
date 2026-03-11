import pytest

from typed_mock import FOREVER, Mocker

from .common import F, ff


def test_mocking_local_function() -> None:
    mocker = Mocker()

    def qq() -> int:
        """ds"""
        return 3

    assert qq() == 3

    mocker.when(qq).return_(4, times=FOREVER)

    assert qq() == 4
    with pytest.raises(TypeError):
        assert qq(43) == 4  # type: ignore[call-arg]

    assert qq.__doc__ == 'ds'
    assert qq.__name__ == 'qq'

    mocker.unpatch_global()
    assert qq() == 3


def test_context_manager() -> None:
    def qq() -> int:
        return 3

    with Mocker() as mocker:
        mocker.when(qq).return_(4, times=2)
        assert qq() == 4

    assert qq() == 3


def test_mocking_global() -> None:
    assert ff() == 5
    with Mocker() as mocker:
        mocker.when(ff).return_(4, times=2)
        assert ff() == 4
    assert ff() == 5


def test_mocking_static_method() -> None:
    with Mocker() as mocker:
        f = F()  # Default (not mocked) class
        mocker.when(f.st).return_(10)
        assert f.st(1) == 10

    assert f.st(1) == 5
