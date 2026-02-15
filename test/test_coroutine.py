import pytest

from typed_mock import Mocker


class F:
    async def g(self, x: int) -> int:
        return 3 + x


class FError(Exception):
    pass


@pytest.mark.asyncio
async def test_async_function() -> None:
    mocker = Mocker()
    f = mocker.mock(F)

    mocker.when(f.g).return_(3)
    assert await f.g(4) == 3

    mocker.when(f.g).called_with(3, return_=2)
    assert await f.g(3) == 2

    mocker.when(f.g).raise_(FError)
    coro = f.g(4)  # Should not raise before awaited
    with pytest.raises(FError):
        await coro

    mocker.when(f.g).raise_(FError)
    with pytest.raises(FError):
        await f.g(4)
