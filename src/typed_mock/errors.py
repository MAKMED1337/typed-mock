from .common import NOT_SET


class MockingError(Exception):
    pass


class TestError(BaseException):
    pass


class InvalidArgumentsToCalledWithError(MockingError):
    pass


class ValueIsNotSetError(TestError):
    pass


class FieldAccessedError(TestError):
    pass


class CalledWithWrongValueError(TestError):
    name: str
    got: object | NOT_SET
    expected: object | NOT_SET

    def __init__(self, name: str, got: object | NOT_SET, expected: object, *args: object) -> None:
        self.name = name
        self.got = got
        self.expected = expected
        super().__init__(*args)
