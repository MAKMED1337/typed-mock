from collections.abc import Callable, Generator
from typing import Any

from pydantic import BaseModel, ConfigDict, TypeAdapter, ValidationError

from .common import ValidationConfig
from .errors import FunctionNotFoundError, InvalidProducerError, ValueIsNotSetError
from .impl import (
    raise_impl,
    return_impl,
)

type FakeMethod = Callable[..., Any]
type Producer = Generator[FakeMethod]


class FakeMethodMember[**P, R]:
    def __init__(self, original_method: Callable[P, R] | None) -> None:
        self.__producers: list[Producer] = []
        self.__original_method = original_method

    def add_producer(self, producer: Producer) -> None:
        self.__producers.append(producer)

    def __call__(self, *args: object, **kwargs: object) -> object:
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


class Data[T](BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    cls: type[T]
    config: ValidationConfig
    fake_methods: dict[str, FakeMethodMember[Any, Any]]


class Mock[T]:
    def __init__(self, cls: type[T], config: ValidationConfig) -> None:
        self.__data = Data[T](cls=cls, config=config, fake_methods={})

    def __get_original_function(self, name: str) -> Any | None:  # noqa: ANN401
        data = self.__data
        try:
            func = getattr(data.cls, name)
        except AttributeError as e:
            if data.config.validate_function_existance:
                raise FunctionNotFoundError from e
            return None

        if callable(func):
            return func

        if data.config.validate_function_existance:
            raise FunctionNotFoundError
        return None

    def __setattr__(self, name: str, value: object) -> None:
        if name in ('_Mock__data', '__orig_class__'):
            super().__setattr__(name, value)
            return

        ta: TypeAdapter[Producer] = TypeAdapter(Producer, config={'arbitrary_types_allowed': True})
        try:
            producer = ta.validate_python(value)
        except ValidationError as e:
            raise InvalidProducerError from e

        data = self.__data

        original_method = self.__get_original_function(name)

        fake_methods = data.fake_methods
        fake_methods.setdefault(name, FakeMethodMember(original_method)).add_producer(producer)

    def __getattr__(self, name: str) -> object:
        data = self.__data

        original_method = self.__get_original_function(name)

        producers = data.fake_methods
        return producers.setdefault(name, FakeMethodMember(original_method))


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
