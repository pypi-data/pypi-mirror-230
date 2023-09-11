from fastapi import HTTPException
from starlette import status


class BadRequestException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status.HTTP_400_BAD_REQUEST, message)
