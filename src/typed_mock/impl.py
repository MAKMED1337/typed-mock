from collections.abc import Callable, Generator

from .common import FOREVER


def _make_callable[**P, R](value: R) -> Callable[P, R]:
    return lambda *_, **__: value


def _make_raise[**P, R, E: BaseException](error: E | type[E]) -> Callable[P, R]:
    def func(*_: P.args, **__: P.kwargs) -> R:
        raise error

    return func


def _make_generator[T](obj: T, times: int) -> Generator[T]:
    if times < -1 or times == 0:
        msg = f'Times should be either positive integer or FOREVER (-1), got: {times}'
        raise ValueError(msg)

    def generator() -> Generator[T]:
        if times == FOREVER:
            while True:
                yield obj
        else:
            for _ in range(times):
                yield obj

    return generator()


def return_impl[**P, R](value: R, *, times: int = 1) -> Generator[Callable[P, R]]:
    return _make_generator(_make_callable(value), times=times)


def raise_impl[**P, R, E: BaseException](error: E | type[E], *, times: int = 1) -> Generator[Callable[P, R]]:
    return _make_generator(_make_raise(error), times=times)
