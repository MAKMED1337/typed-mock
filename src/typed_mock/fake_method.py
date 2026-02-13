import inspect
from collections.abc import Awaitable, Callable, Generator
from inspect import Signature

from .common import ValidationConfig
from .errors import ValueIsNotSetError

type FakeMethod[**P, R] = Callable[P, R]
type Producer[**P, R] = Generator[FakeMethod[P, R]]


def _make_coro[**P, R](func: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> Awaitable[R]:
    async def inner() -> R:
        return func(*args, **kwargs)

    return inner()


class FakeMethodMember[**P, R]:
    def __init__(self, original_method: Callable[P, R], config: ValidationConfig) -> None:
        self.__producers: list[Producer[P, R]] = []
        self.__original_method = original_method
        self.__config = config

    def add_producer(self, producer: Producer[P, R]) -> None:
        self.__producers.append(producer)

    @property
    def signature(self) -> Signature:
        return inspect.signature(self.__original_method)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> object:
        sig = self.signature
        if self.__config.validate_call_arguments and sig:
            sig.bind(*args, **kwargs)

        producers = self.__producers
        while producers:
            producer = producers[0]
            try:
                func = next(producer)
            except StopIteration:
                producers.pop(0)
            else:
                if inspect.iscoroutinefunction(self.__original_method):
                    return _make_coro(func, *args, **kwargs)  # We do not want to have side effects before awaiting
                return func(*args, **kwargs)
        raise ValueIsNotSetError
