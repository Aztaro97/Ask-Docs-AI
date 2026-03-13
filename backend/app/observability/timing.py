"""Timing decorator for measuring operation durations."""

import time
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from app.observability.logging import get_logger

P = ParamSpec("P")
T = TypeVar("T")

logger = get_logger(__name__)


def timed(operation: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to measure and log operation timing.

    Args:
        operation: Name of the operation being timed (e.g., "ingestion", "retrieval")

    Usage:
        @timed("retrieval")
        async def retrieve_documents(query: str) -> list[Document]:
            ...
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)  # type: ignore
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.info(
                    f"{operation}_completed",
                    operation=operation,
                    duration_ms=round(elapsed_ms, 2),
                    status="success",
                )
                return result
            except Exception as e:
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.error(
                    f"{operation}_failed",
                    operation=operation,
                    duration_ms=round(elapsed_ms, 2),
                    status="error",
                    error=str(e),
                )
                raise

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.info(
                    f"{operation}_completed",
                    operation=operation,
                    duration_ms=round(elapsed_ms, 2),
                    status="success",
                )
                return result
            except Exception as e:
                elapsed_ms = (time.perf_counter() - start) * 1000
                logger.error(
                    f"{operation}_failed",
                    operation=operation,
                    duration_ms=round(elapsed_ms, 2),
                    status="error",
                    error=str(e),
                )
                raise

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore
        return sync_wrapper

    return decorator


class TimingContext:
    """Context manager for timing code blocks."""

    def __init__(self, operation: str):
        self.operation = operation
        self.start: float = 0
        self.elapsed_ms: float = 0

    def __enter__(self) -> "TimingContext":
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        self.elapsed_ms = (time.perf_counter() - self.start) * 1000
        logger.info(
            f"{self.operation}_completed",
            operation=self.operation,
            duration_ms=round(self.elapsed_ms, 2),
        )
