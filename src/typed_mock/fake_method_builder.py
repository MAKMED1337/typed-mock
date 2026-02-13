from collections.abc import Awaitable
from typing import overload

from .common import Args
from .fake_method import FakeMethodMember
from .impl import called_with_full_impl, called_with_partial_impl, raise_impl, return_impl


class FakeMethodBuilder[**P, R]:
    def __init__(self, fake_method: FakeMethodMember[P, R | Awaitable[R]]) -> None:
        self.__fake_method = fake_method

    @overload
    def return_(self, /, *values: R) -> 'FakeMethodBuilder[P, R]': ...
    @overload
    def return_(self, value: R, /, *, times: int = 1) -> 'FakeMethodBuilder[P, R]': ...

    def return_(self, /, *values: R, times: int = 1) -> 'FakeMethodBuilder[P, R]':
        if not values:
            raise ValueError('No values specified')
        if len(values) > 1 and times != 1:
            raise ValueError('Cannot set more than 1 value and times at the same time')

        if len(values) > 1:
            for value in values:
                self.__fake_method.add_producer(return_impl(value))
        else:
            value = values[0]  # pyright: ignore[reportGeneralTypeIssues]
            self.__fake_method.add_producer(return_impl(value, times=times))
        return self

    def raise_[E: BaseException](self, error: E | type[E], *, times: int = 1) -> 'FakeMethodBuilder[P, R]':
        self.__fake_method.add_producer(raise_impl(error, times=times))
        return self

    def called_with(self, *args: object, return_: R, **kwargs: object) -> 'FakeMethodBuilder[P, R]':
        return self.called_with_partial(*args, return_=return_, **kwargs)

    def called_with_partial(self, *args: object, return_: R, **kwargs: object) -> 'FakeMethodBuilder[P, R]':
        self.__fake_method.add_producer(called_with_partial_impl(args, kwargs, return_, self.__fake_method.signature))
        return self

    def called_with_full(self, args: Args[P], return_: R) -> 'FakeMethodBuilder[P, R]':
        self.__fake_method.add_producer(called_with_full_impl(args, return_, self.__fake_method.signature))
        return self
