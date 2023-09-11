
from typing import Tuple, Union, Optional

from fastapi.exceptions import RequestValidationError
from pydantic.error_wrappers import ErrorWrapper

from ..enums.error_type_enum import ErrorType
from ..exceptions.custom_error_factory import CustomErrorGenerator


def throw_validation_field(
    fields: Optional[Union[str, Tuple[Union[int, str], ...]]] = (),
    code: Optional[str] = None,
):
    if code is None:
        return RequestValidationError([ErrorWrapper(ValueError(), fields)])

    exception = CustomErrorGenerator(error_type=ErrorType.VALUE_ERROR, code=code).generate_error()
    return RequestValidationError([ErrorWrapper(exception, fields)])


def throw_validation_field_with_exception(
    exception: Exception, fields: Optional[Union[str, Tuple[Union[int, str], ...]]] = ()
):
    return RequestValidationError([ErrorWrapper(exception, fields)])
