import pytest

from typed_mock import FunctionNotFoundError, Mocker, ValidationConfig


class F:
    g = 43

    def f(self) -> int:
        return 3


def test_mocking_nonfunction() -> None:
    mocker = Mocker()
    f = mocker.mock(F)
    with pytest.raises(FunctionNotFoundError):
        mocker.when(f.g)  # type: ignore[arg-type]

    mocker2 = Mocker(ValidationConfig(validate_function_existance=False))
    f = mocker2.mock(F)
    mocker2.when(f.k)  # type: ignore[attr-defined]


def test_nonexistent_method() -> None:
    mocker = Mocker()

    f = mocker.mock(F)

    with pytest.raises(FunctionNotFoundError):
        mocker.when(f.k).return_(5)  # type: ignore[attr-defined]

    mocker2 = Mocker(ValidationConfig(validate_function_existance=False))
    f = mocker2.mock(F)
    mocker.when(f.k).return_(6)  # type: ignore[attr-defined]
