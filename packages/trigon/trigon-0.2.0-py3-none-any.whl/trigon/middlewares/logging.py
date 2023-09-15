from loguru import logger
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from trigon.core.middleware import Middleware


class LoggingMiddleware(Middleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            logger.debug(f"{request.method} {request.url}")

            response = await call_next(request)

            logger.debug(f"{request.method} {request.url} {response.status_code}")
        except Exception as exception:
            logger.exception(exception)

            raise

        return response
