
from typed_mock import FOREVER, Mocker

from .common import F


def _test_mocking_class_method() -> None:
    with Mocker() as mocker:
        f = F()
        g = F()

        # This should **NOT** interfere with instance g
        mocker.when(f.cl).return_(10, times=FOREVER)
        assert g.cl(2) == 45


def _test_mocking_static_method() -> None:
    with Mocker() as mocker:
        f = F()
        g = F()

        # This should **NOT** interfere with instance g
        mocker.when(f.st).return_(10)
        assert g.st(2) == 6
