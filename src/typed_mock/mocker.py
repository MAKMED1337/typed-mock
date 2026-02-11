from collections.abc import Callable

from .common import ValidationConfig
from .funcs import FakeMethodMember, Mock, ProducerBuilder


class Mocker:
    def __init__(self, config: ValidationConfig | None = None) -> None:
        if config is None:
            config = ValidationConfig()

        self.config = config

    def mock[T](self, cls: type[T]) -> T:
        return Mock[T](cls, self.config)  # type: ignore[return-value]

    def when[**P, R](self, func: Callable[P, R]) -> ProducerBuilder[P, R]:
        if not isinstance(func, FakeMethodMember):
            msg = f'Invalid argument to function `when`, expected class method, got: {type(func)}'
            raise TypeError(msg)

        return ProducerBuilder(func)
