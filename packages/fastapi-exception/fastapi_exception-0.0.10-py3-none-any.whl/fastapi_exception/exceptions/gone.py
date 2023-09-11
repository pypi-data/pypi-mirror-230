from fastapi import HTTPException
from starlette import status


class GoneException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status.HTTP_410_GONE, message)
