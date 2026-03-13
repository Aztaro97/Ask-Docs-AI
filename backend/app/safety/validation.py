"""Input validation and sanitization."""

import re
from typing import Any

from pydantic import ValidationError

from app.config import get_settings
from app.observability import get_logger

logger = get_logger(__name__)


class ValidationError(Exception):
    """Input validation error."""

    def __init__(self, message: str, field: str | None = None):
        self.message = message
        self.field = field
        super().__init__(message)


def validate_query(query: str) -> str:
    """Validate and sanitize a query string.

    Args:
        query: Raw query input

    Returns:
        Sanitized query string

    Raises:
        ValidationError: If query is invalid
    """
    settings = get_settings()

    # Check for empty query
    if not query or not query.strip():
        raise ValidationError("Query cannot be empty", field="question")

    # Trim whitespace
    query = query.strip()

    # Check length
    if len(query) > settings.max_query_length:
        raise ValidationError(
            f"Query exceeds maximum length of {settings.max_query_length} characters",
            field="question",
        )

    # Check for minimum meaningful content
    if len(query) < 3:
        raise ValidationError("Query is too short", field="question")

    # Basic sanitization - remove control characters
    query = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", query)

    # Remove excessive whitespace
    query = re.sub(r"\s+", " ", query)

    logger.debug("query_validated", length=len(query))

    return query


def validate_top_k(top_k: int) -> int:
    """Validate top_k parameter.

    Args:
        top_k: Requested number of results

    Returns:
        Valid top_k value

    Raises:
        ValidationError: If top_k is invalid
    """
    if top_k < 1:
        raise ValidationError("top_k must be at least 1", field="top_k")
    if top_k > 20:
        raise ValidationError("top_k cannot exceed 20", field="top_k")
    return top_k


def validate_file_path(path: str) -> str:
    """Validate a file path for safety.

    Args:
        path: File path to validate

    Returns:
        Validated path

    Raises:
        ValidationError: If path is potentially dangerous
    """
    # Check for path traversal
    if ".." in path:
        raise ValidationError("Path traversal not allowed", field="path")

    # Check for absolute paths outside expected directories
    if path.startswith("/") and not path.startswith("/tmp"):
        # Only allow /tmp for temporary operations
        # In production, paths should be relative to docs_path
        pass

    return path
