from collections.abc import Callable

from .common import ValidationConfig
from .fake_method_builder import FakeMethodBuilder
from .funcs import FakeMethodMember
from .mock import create_mock


class Mocker:
    def __init__(self, config: ValidationConfig | None = None) -> None:
        if config is None:
            config = ValidationConfig()

        self.config = config

    def mock[T](self, cls: type[T]) -> T:
        return create_mock(cls, self.config)

    def when[**P, R](self, func: Callable[P, R]) -> FakeMethodBuilder[P, R]:
        if not isinstance(func, FakeMethodMember):
            msg = f'Invalid argument to function `when`, expected class method, got: {type(func)}'
            raise TypeError(msg)

        return FakeMethodBuilder(func)
