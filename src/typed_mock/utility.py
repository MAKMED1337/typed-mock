from collections.abc import Callable, Generator


def _make_callable[**P, R](value: R) -> Callable[P, R]:
    return lambda *_, **__: value


def _make_raise[**P, R, E: BaseException](error: E | type[E]) -> Callable[P, R]:
    def func(*_: P.args, **__: P.kwargs) -> R:
        raise error

    return func


def _make_generator_once[T](obj: T) -> Generator[T]:
    def generator() -> Generator[T]:
        yield obj

    return generator()


def _make_generator_forever[T](obj: T) -> Generator[T]:
    def generator() -> Generator[T]:
        while True:
            yield obj

    return generator()


def return_once_impl[**P, R](value: R) -> Generator[Callable[P, R]]:
    return _make_generator_once(_make_callable(value))


def return_forever_impl[**P, R](value: R) -> Generator[Callable[P, R]]:
    return _make_generator_forever(_make_callable(value))


def raise_once_impl[**P, R, E: BaseException](error: E | type[E]) -> Generator[Callable[P, R]]:
    return _make_generator_once(_make_raise(error))


def raise_forever_impl[**P, R, E: BaseException](error: E | type[E]) -> Generator[Callable[P, R]]:
    return _make_generator_forever(_make_raise(error))
