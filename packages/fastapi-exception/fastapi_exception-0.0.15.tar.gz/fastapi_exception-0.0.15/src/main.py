
from fastapi import FastAPI

from .fastapi_exception.fastapi_exception_config import FastApiException
from .config.i18n import i18n_service

app = FastAPI(title="Test App")

FastApiException.config(app, i18n_service)
