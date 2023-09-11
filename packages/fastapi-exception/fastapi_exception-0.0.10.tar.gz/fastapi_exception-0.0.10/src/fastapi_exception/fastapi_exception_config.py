from fastapi import FastAPI, HTTPException
from typing import Any, Optional, Tuple, Union
from keycloak import KeycloakAuthenticationError, KeycloakPostError
from requests import RequestException
from pydantic import ValidationError
from starlette import status
from starlette.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .exceptions.direct_response import DirectResponseException
from .handlers.global_exception_handler import http_global_exception_handler
from .handlers.http_exception_handler import http_exception_handler, http_direct_response_handler
from .handlers.key_cloak_exception_handler import keycloak_exception_handler, keycloak_post_exception_handler
from .handlers.request_exception_handler import request_exception_handler


async def validation_exception_handler(request, error: ValidationError):  # pylint: disable=unused-argument
    response = {'message': 'Validation error', 'errors': translate_errors(error.errors())}
    return JSONResponse(response, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


def build_constraint_index(constraints: dict, ctx: Optional):
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

        error['msg'] = FastApiException.i18n_service.translate(f'validation.{error_type}', **constraints)

    return errors


class FastApiException:
    i18n_service: Any = None

    @staticmethod
    def config(app: FastAPI, i18n_service: Any):
        return FastApiException(app, i18n_service)

    def __init__(self, app: FastAPI, i18n_service: Any):
        FastApiException.i18n_service = i18n_service

        app.exception_handler(Exception)(http_global_exception_handler)
        app.exception_handler(HTTPException)(http_exception_handler)
        app.exception_handler(DirectResponseException)(http_direct_response_handler)
        app.exception_handler(RequestValidationError)(validation_exception_handler)
        app.exception_handler(RequestException)(request_exception_handler)
        app.exception_handler(KeycloakAuthenticationError)(keycloak_exception_handler)
        app.exception_handler(KeycloakPostError)(keycloak_post_exception_handler)
