from pydantic import BaseModel

FOREVER = -1


class ValidationConfig(BaseModel):
    raise_on_field_access: bool = True  # Any callable is considered to be a non attribute
    validate_call_arguments: bool = True
