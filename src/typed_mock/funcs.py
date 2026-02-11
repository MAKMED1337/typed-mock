import inspect
from collections.abc import Callable, Generator

from .common import ValidationConfig
from .errors import ValueIsNotSetError
from .impl import raise_impl, return_impl

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


class ProducerBuilder[**P, R]:
    def __init__(self, fake_method: FakeMethodMember[P, R]) -> None:
        self.fake_method = fake_method

    def return_(self, *values: R, times: int = 1) -> 'ProducerBuilder[P, R]':
        if not values:
            raise ValueError('No values specified')
        if len(values) > 1 and times != 1:
            raise ValueError('Cannot set more than 1 value and times at the same time')

        if len(values) > 1:
            for value in values:
                self.fake_method.add_producer(return_impl(value))
        else:
            value = values[0]  # pyright: ignore[reportGeneralTypeIssues]
            self.fake_method.add_producer(return_impl(value, times=times))
        return self

    def raise_[E: BaseException](self, error: E | type[E], *, times: int = 1) -> 'ProducerBuilder[P, R]':
        self.fake_method.add_producer(raise_impl(error, times=times))
        return self
