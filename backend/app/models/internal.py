"""Internal data models for document processing."""

import hashlib
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, computed_field


class ChunkMetadata(BaseModel):
    """Metadata attached to each chunk."""

    doc_id: str = Field(..., description="Document identifier")
    chunk_id: int = Field(..., description="Chunk index within document")
    file_path: str = Field(..., description="Original file path")
    content_hash: str = Field(..., description="SHA256 hash of chunk content")
    embedding_model: str = Field(..., description="Embedding model used")
    embedding_version: str = Field(..., description="Embedding model version")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    extra: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class Document(BaseModel):
    """A loaded document before chunking."""

    doc_id: str = Field(..., description="Unique document identifier")
    file_path: str = Field(..., description="Path to source file")
    content: str = Field(..., description="Full document content")
    file_type: str = Field(..., description="File extension/type")
    file_size: int = Field(..., description="File size in bytes")
    loaded_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    @property
    def content_hash(self) -> str:
        """SHA256 hash of document content."""
        return hashlib.sha256(self.content.encode()).hexdigest()[:16]


class Chunk(BaseModel):
    """A chunk of text from a document."""

    content: str = Field(..., description="Chunk text content")
    metadata: ChunkMetadata = Field(..., description="Chunk metadata")

    @computed_field
    @property
    def token_count(self) -> int:
        """Approximate token count (rough estimate: 4 chars per token)."""
        return len(self.content) // 4


class RetrievedChunk(BaseModel):
    """A chunk retrieved from the vector store with relevance score."""

    chunk: Chunk = Field(..., description="The retrieved chunk")
    score: float = Field(..., ge=0, description="Relevance/similarity score")
    rank: int = Field(..., description="Rank in retrieval results")

    @property
    def metadata(self) -> ChunkMetadata:
        """Shortcut to chunk metadata."""
        return self.chunk.metadata

    @property
    def content(self) -> str:
        """Shortcut to chunk content."""
        return self.chunk.content
