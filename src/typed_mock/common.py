from pydantic import BaseModel

FOREVER = -1


class NOT_SET:  # noqa: N801
    pass


class ValidationConfig(BaseModel):
    raise_on_field_access: bool = True  # Any callable is considered to be a non attribute
    validate_call_arguments: bool = True


class Args[**P]:
    def __init__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        self.args = args
        self.kwargs = kwargs
