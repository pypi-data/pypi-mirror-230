from fastapi import HTTPException
from starlette import status
from starlette.responses import JSONResponse

from ..exceptions.direct_response import DirectResponseException


async def http_exception_handler(request, error: HTTPException):  # pylint: disable=unused-argument
    response = {'message': error.detail}
    if error.detail == 'Not authenticated':
        return JSONResponse(response, status_code=status.HTTP_401_UNAUTHORIZED)
    return JSONResponse(response, status_code=error.status_code)


async def http_direct_response_handler(request, error: DirectResponseException):  # pylint: disable=unused-argument
    return JSONResponse(error.message, status_code=status.HTTP_200_OK)
