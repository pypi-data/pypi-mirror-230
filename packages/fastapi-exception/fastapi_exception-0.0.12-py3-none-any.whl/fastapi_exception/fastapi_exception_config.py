from fastapi import FastAPI, HTTPException
from typing import Any
from keycloak import KeycloakAuthenticationError, KeycloakPostError
from requests import RequestException
from fastapi.exceptions import RequestValidationError
from fastapi_global_variable import GlobalVariable

from .exceptions.direct_response import DirectResponseException
from .handlers.global_exception_handler import http_global_exception_handler
from .handlers.http_exception_handler import http_exception_handler, http_direct_response_handler
from .handlers.key_cloak_exception_handler import keycloak_exception_handler, keycloak_post_exception_handler
from .handlers.request_exception_handler import request_exception_handler
from .handlers.validation_exception_handler import validation_exception_handler


class FastApiException:
    i18n_service: Any = None

    @staticmethod
    def config(app: FastAPI, i18n_service: Any):
        return FastApiException(app, i18n_service)

    def __init__(self, app: FastAPI, i18n_service: Any):
        GlobalVariable.set('i18n_service', i18n_service)

        app.exception_handler(Exception)(http_global_exception_handler)
        app.exception_handler(HTTPException)(http_exception_handler)
        app.exception_handler(DirectResponseException)(http_direct_response_handler)
        app.exception_handler(RequestValidationError)(validation_exception_handler)
        app.exception_handler(RequestException)(request_exception_handler)
        app.exception_handler(KeycloakAuthenticationError)(keycloak_exception_handler)
        app.exception_handler(KeycloakPostError)(keycloak_post_exception_handler)
