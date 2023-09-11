from fastapi import HTTPException
from starlette import status


class ForbiddenException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status.HTTP_403_FORBIDDEN, message)
