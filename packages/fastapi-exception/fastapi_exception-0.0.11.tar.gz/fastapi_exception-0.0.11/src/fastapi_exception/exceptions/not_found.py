from fastapi import HTTPException
from starlette import status


class NotfoundException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status.HTTP_404_NOT_FOUND, message)
