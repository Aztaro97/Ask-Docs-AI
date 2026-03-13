"""API middleware for request tracking, timing, and rate limiting."""

import time
import uuid
from collections.abc import Callable

from fastapi import FastAPI, Request, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.observability.logging import get_logger, set_request_id

logger = get_logger(__name__)


def get_limiter() -> Limiter:
    """Create rate limiter instance."""
    return Limiter(key_func=get_remote_address)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID and timing to all requests."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or use existing request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:8]
        set_request_id(request_id)

        # Start timing
        start_time = time.perf_counter()

        # Log request start
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown",
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=round(elapsed_ms, 2),
                error=str(e),
            )
            raise

        # Calculate duration
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = str(round(elapsed_ms, 2))

        # Log request completion
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(elapsed_ms, 2),
        )

        return response


def setup_middleware(app: FastAPI) -> None:
    """Configure all middleware for the application."""
    settings = get_settings()

    # Rate limiting
    limiter = get_limiter()
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Request context (request ID, timing)
    app.add_middleware(RequestContextMiddleware)

    # CORS for frontend
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Response-Time-Ms"],
    )
