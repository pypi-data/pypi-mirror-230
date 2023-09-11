from fastapi import HTTPException
from pydantic import BaseModel
from starlette import status


class EntityNotFoundException(HTTPException):
    def __init__(self, model: BaseModel):
        self.model = model
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            f'{model.__name__} not found'.replace('Entity', ''),
        )
