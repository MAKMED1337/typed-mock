from typing import cast

from .common import ValidationConfig
from .errors import FieldAccessedError
from .funcs import FakeMethodMember


class Mock[T]:
    def __init__(self, cls: type[T], config: ValidationConfig) -> None:
        self.__obj = object.__new__(cls)
        self.__config = config
        self.__fake_methods: dict[str, FakeMethodMember[..., object]] = {}

    def __getattribute__(self, name: str, /) -> object:
        if name in ('_Mock__obj', '_Mock__config', '_Mock__fake_methods'):
            return super().__getattribute__(name)

        result = self.__obj.__getattribute__(name)
        config = self.__config

        if callable(result):
            return self.__fake_methods.setdefault(name, FakeMethodMember(result, config))

        if config.raise_on_field_access:
            raise FieldAccessedError
        return result


def create_mock[T](cls: type[T], config: ValidationConfig) -> T:
    mock = Mock(cls, config)
    return cast('T', mock)
