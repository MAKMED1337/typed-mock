from collections.abc import Callable, Generator
from inspect import Signature

from .common import FOREVER, NOT_SET, Args
from .errors import CalledWithWrongValueError, InvalidArgumentsToCalledWithError


def _make_callable[**P, R](value: R) -> Callable[P, R]:
    return lambda *_, **__: value


def _make_callable_validate_args_partial[**P, R](
    args: tuple[object, ...], kwargs: dict[str, object], return_: R, sig: Signature
) -> Callable[P, R]:
    try:
        expected_arguments = sig.bind_partial(*args, **kwargs).arguments
    except TypeError as e:
        raise InvalidArgumentsToCalledWithError from e

    def validate_args(*args: P.args, **kwargs: P.kwargs) -> R:
        bound_arguments = sig.bind(*args, **kwargs).arguments
        for name, expected in expected_arguments.items():
            got = bound_arguments.get(name, NOT_SET)
            if got != expected:
                raise CalledWithWrongValueError(name=name, got=got, expected=expected)
        return return_

    return validate_args


def _make_callable_validate_args_full[**P, R](args: Args[P], return_: R, sig: Signature) -> Callable[P, R]:
    try:
        expected_arguments = sig.bind(*args.args, **args.kwargs).arguments
    except TypeError as e:
        raise InvalidArgumentsToCalledWithError from e

    def validate_args(*args: P.args, **kwargs: P.kwargs) -> R:
        bound_arguments = sig.bind(*args, **kwargs).arguments
        if bound_arguments != expected_arguments:
            for name in list(bound_arguments.keys()) + list(expected_arguments.keys()):
                expected = expected_arguments.get(name, NOT_SET)
                got = bound_arguments.get(name, NOT_SET)
                if expected != got:
                    raise CalledWithWrongValueError(name=name, got=got, expected=expected)
        return return_

    return validate_args


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


def called_with_partial_impl[**P, R](
    args: tuple[object, ...], kwargs: dict[str, object], return_: R, sig: Signature
) -> Generator[Callable[P, R]]:
    return _make_generator(_make_callable_validate_args_partial(args, kwargs, return_, sig), times=1)


def called_with_full_impl[**P, R](args: Args[P], return_: R, sig: Signature) -> Generator[Callable[P, R]]:
    return _make_generator(_make_callable_validate_args_full(args, return_, sig), times=1)
