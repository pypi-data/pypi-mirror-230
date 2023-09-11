from typing import Any, Optional, Tuple, Union
from fastapi_global_variable import GlobalVariable

from pydantic import ValidationError
from starlette import status
from starlette.responses import JSONResponse


async def validation_exception_handler(request, error: ValidationError):  # pylint: disable=unused-argument
    response = {'message': 'Validation error', 'errors': translate_errors(error.errors())}
    return JSONResponse(response, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


def build_constraint_index(constraints: dict, ctx: Optional[Any]):
    if not ctx:
        return

    for index, key in enumerate(ctx.keys()):
        constraints[f'constraint{index + 1}'] = ctx[key]


def override_list_property_constraint(constraints: dict, loc: Tuple[Union[int, str], ...]):
    if isinstance(constraints.get('property'), int):
        constraints['property'] = f'{loc[-2]}[{loc[-1]}]'


def translate_errors(errors: list[Any]):
    for error in errors:
        loc, ctx, error_type = error['loc'], error.get('ctx'), error['type']

        constraints = {'property': loc[-1]}
        override_list_property_constraint(constraints, loc)
        build_constraint_index(constraints, ctx)

        error['msg'] = GlobalVariable.get_or_fail('translator_service').translate(f'validation.{error_type}', **constraints)

    return errors
