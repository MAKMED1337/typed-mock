from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Self, overload

from typed_mock.patched import PATCHED_FUNCTIONS

from .common import ValidationConfig
from .fake_function import FakeFunction
from .fake_function_builder import FakeFunctionBuilder
from .mock import create_mock

if TYPE_CHECKING:
    from types import MethodType


class Mocker:
    def __init__(self, config: ValidationConfig | None = None) -> None:
        if config is None:
            config = ValidationConfig()

        self.config = config
        self.patched_class_methods: list[MethodType] = []

    def mock[T](self, cls: type[T]) -> T:
        return create_mock(cls, self.config)

    @overload
    def when[**P, R](self, func: Callable[P, Awaitable[R]]) -> FakeFunctionBuilder[P, R]: ...
    @overload
    def when[**P, R](self, func: Callable[P, R]) -> FakeFunctionBuilder[P, R]: ...

    def when[**P, R](self, func: Callable[P, R | Awaitable[R]]) -> FakeFunctionBuilder[P, R]:
        fake = func if isinstance(func, FakeFunction) else FakeFunction(func, self.config, self)
        return FakeFunctionBuilder(fake)

    def unpatch(self) -> None:
        for func, original_code, _fake in PATCHED_FUNCTIONS.get(id(self), []):
            func.__code__ = original_code

        for func in self.patched_class_methods:
            setattr(func.__self__, func.__name__, func)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.unpatch()
