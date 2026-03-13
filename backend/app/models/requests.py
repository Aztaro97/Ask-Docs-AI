"""Request models for API endpoints."""

from pydantic import BaseModel, Field


class IndexRequest(BaseModel):
    """Request to index documents from a directory."""

    path: str | None = Field(
        default=None,
        description="Path to documents directory. Uses default docs/ if not specified.",
    )
    force_reindex: bool = Field(
        default=False,
        description="Force re-indexing even if documents haven't changed.",
    )


class QueryRequest(BaseModel):
    """Request to query the indexed documents."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="The question to answer based on indexed documents.",
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of relevant chunks to retrieve.",
    )
    stream: bool = Field(
        default=True,
        description="Whether to stream the response via SSE.",
    )
