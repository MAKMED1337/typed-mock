from pydantic import BaseModel

FOREVER = -1


class ValidationConfig(BaseModel):
    validate_function_existance: bool = True
    validate_call_arguments: bool = True
