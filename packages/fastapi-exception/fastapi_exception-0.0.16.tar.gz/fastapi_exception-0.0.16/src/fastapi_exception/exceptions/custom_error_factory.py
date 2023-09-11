from pydantic import PydanticValueError, PydanticTypeError

from ..enums.error_type_enum import ErrorType


class CustomErrorGenerator:
    def __init__(
        self,
        error_type: ErrorType,
        code: str,
        msg_template="{code}",
        class_name=None,
    ):
        self.error_type = error_type
        self.code = code
        self.class_name = class_name or f"{code.title().replace('.', '').replace('_', '')}Error"
        self.msg_template = msg_template.format(code=code)

    def generate_error(self):
        error_class = (PydanticValueError,) if self.error_type == ErrorType.VALUE_ERROR else (PydanticTypeError,)
        return type(
            self.class_name,
            error_class,
            {"code": self.code, "msg_template": self.msg_template},
        )()
