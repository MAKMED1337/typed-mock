import inspect
from collections.abc import Callable, Generator

from .common import ValidationConfig
from .errors import ValueIsNotSetError

type FakeMethod[**P, R] = Callable[P, R]
type Producer[**P, R] = Generator[FakeMethod[P, R]]


class FakeMethodMember[**P, R]:
    def __init__(self, original_method: Callable[P, R] | None, config: ValidationConfig) -> None:
        self.__producers: list[Producer[P, R]] = []
        self.__original_method = original_method
        self.__config = config

    def add_producer(self, producer: Producer[P, R]) -> None:
        self.__producers.append(producer)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> object:
        if self.__config.validate_call_arguments and self.__original_method:
            sig = inspect.signature(self.__original_method)
            sig.bind(*args, **kwargs)

        producers = self.__producers
        while producers:
            producer = producers[0]
            try:
                func = next(producer)
            except StopIteration:
                producers.pop(0)
            else:
                return func(*args, **kwargs)
        raise ValueIsNotSetError
