from typed_mock import Mocker

from .common import F

f = F()


def test_mocked_bound_method_is_restored_after_context() -> None:
    with Mocker() as mocker:
        mocker.when(f.g).called_with(1, return_=42)

        assert f.g(1, 2) == 42

    assert f.g(1, 2) == 3


def test_next_test_sees_original_bound_method() -> None:
    assert f.g(1, 2) == 3
