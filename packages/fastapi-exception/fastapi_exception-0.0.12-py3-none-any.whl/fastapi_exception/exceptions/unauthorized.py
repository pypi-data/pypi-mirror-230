from fastapi import HTTPException
from starlette import status


class UnauthorizedException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status.HTTP_401_UNAUTHORIZED, message)
