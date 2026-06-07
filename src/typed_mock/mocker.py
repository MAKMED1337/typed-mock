from collections.abc import Awaitable, Callable
from typing import Any, Self, overload

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
        self._patched_methods: list[tuple[object, str, Any]] = []

    def mock[T](self, cls: type[T]) -> T:
        return create_mock(cls, self.config)

    @overload
    def when[**P, R](self, func: Callable[P, Awaitable[R]]) -> FakeFunctionBuilder[P, R]: ...
    @overload
    def when[**P, R](self, func: Callable[P, R]) -> FakeFunctionBuilder[P, R]: ...

    def when[**P, R](self, func: Callable[P, R | Awaitable[R]]) -> FakeFunctionBuilder[P, R]:
        fake = func if isinstance(func, FakeFunction) else FakeFunction(func, self.config, self, self._patch_method)
        return FakeFunctionBuilder(fake)

    def _patch_method(self, target: object, name: str, fake: FakeFunction[..., Any]) -> None:
        if not hasattr(target, name):
            raise AttributeError(name)
        original_value = getattr(target, name)
        self._patched_methods.append((target, name, original_value))
        setattr(target, name, fake)

    def unpatch(self) -> None:
        for func, original_code, _fake in PATCHED_FUNCTIONS.get(id(self), []):
            func.__code__ = original_code

        for target, name, original_value in self._patched_methods:
            setattr(target, name, original_value)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.unpatch()
