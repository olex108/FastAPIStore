# middleware/access_logging.py
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

access_logger = logging.getLogger("access")


class LogMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования запросов"""

    async def dispatch(self, request: Request, call_next):
        access_logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        access_logger.info(f"Response: {response.status_code}")
        return response
