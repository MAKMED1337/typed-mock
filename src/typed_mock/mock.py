from typing import Any, cast

from .common import ValidationConfig
from .errors import AttributeAccessedError
from .funcs import FakeMethodMember


def create_mock[T](cls: type[T], config: ValidationConfig) -> T:
    fake_methods: dict[str, FakeMethodMember[Any, Any]] = {}

    class Mock(cls):  # type: ignore[valid-type, misc]
        def __getattribute__(self, name: str, /) -> object:
            result = super().__getattribute__(name)
            if callable(result):
                return fake_methods.setdefault(name, FakeMethodMember(result, config))

            if config.raise_on_attribute:
                raise AttributeAccessedError
            return result

    mock = object.__new__(Mock)
    return cast('T', mock)
