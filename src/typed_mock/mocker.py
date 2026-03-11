from collections.abc import Awaitable, Callable
from typing import Self, overload

from typed_mock.patched import PATCHED_FUNCTIONS

from .common import ValidationConfig
from .fake_function import FakeFunction
from .fake_function_builder import FakeFunctionBuilder
from .mock import create_mock


class Mocker:
    def __init__(self, config: ValidationConfig | None = None) -> None:
        if config is None:
            config = ValidationConfig()

        self.config = config

    def mock[T](self, cls: type[T]) -> T:
        return create_mock(cls, self.config)

    @overload
    def when[**P, R](self, func: Callable[P, Awaitable[R]]) -> FakeFunctionBuilder[P, R]: ...
    @overload
    def when[**P, R](self, func: Callable[P, R]) -> FakeFunctionBuilder[P, R]: ...

    def when[**P, R](self, func: Callable[P, R | Awaitable[R]]) -> FakeFunctionBuilder[P, R]:
        fake = func if isinstance(func, FakeFunction) else FakeFunction(func, self.config, self)
        return FakeFunctionBuilder(fake)

    def unpatch_global(self) -> None:
        for func, original_code, _fake in PATCHED_FUNCTIONS.get(id(self), []):
            func.__code__ = original_code

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.unpatch_global()
