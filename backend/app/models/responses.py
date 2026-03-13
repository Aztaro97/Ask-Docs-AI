"""Response models for API endpoints."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ErrorType(str, Enum):
    """Types of errors that can occur."""

    MODEL_ERROR = "model"
    RETRIEVAL_ERROR = "retrieval"
    NETWORK_ERROR = "network"
    RATE_LIMIT = "rate_limit"
    VALIDATION_ERROR = "validation"


class CitationResponse(BaseModel):
    """A citation from a source document."""

    id: int = Field(..., description="Citation number (1-indexed)")
    doc_id: str = Field(..., description="Document identifier")
    chunk_id: int = Field(..., description="Chunk index within document")
    file_path: str = Field(..., description="Path to source file")
    snippet: str = Field(..., description="Relevant text snippet")
    score: float = Field(..., ge=0, le=1, description="Relevance score")


class IndexResponse(BaseModel):
    """Response from indexing operation."""

    status: str = Field(..., description="Status of the indexing operation")
    documents_indexed: int = Field(..., description="Number of documents indexed")
    chunks_created: int = Field(..., description="Number of chunks created")
    duration_ms: float = Field(..., description="Time taken in milliseconds")
    errors: list[str] = Field(default=[], description="Any errors encountered")


class QueryResponse(BaseModel):
    """Response from a query (non-streaming)."""

    answer: str = Field(..., description="Generated answer")
    citations: list[CitationResponse] = Field(..., description="Source citations")
    abstained: bool = Field(
        default=False,
        description="Whether the system abstained from answering",
    )
    retrieval_ms: float = Field(..., description="Retrieval time in ms")
    generation_ms: float = Field(..., description="Generation time in ms")
    total_tokens: int = Field(..., description="Approximate tokens used")


class ErrorResponse(BaseModel):
    """Error response structure."""

    type: ErrorType = Field(..., description="Type of error")
    message: str = Field(..., description="Human-readable error message")
    retryable: bool = Field(default=False, description="Whether the request can be retried")
    details: dict[str, Any] | None = Field(default=None, description="Additional error details")


class StreamEvent(BaseModel):
    """SSE event structure."""

    event: str = Field(..., description="Event type: token, citation, done, error")
    data: dict[str, Any] = Field(..., description="Event payload")
