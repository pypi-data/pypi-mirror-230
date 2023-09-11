from starlette import status
from starlette.responses import JSONResponse


async def http_global_exception_handler(request, error: Exception):
    print(error)
    response = {
        'message': 'An error occurred during processing.',
    }
    return JSONResponse(response, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
