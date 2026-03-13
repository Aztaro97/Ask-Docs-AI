"""Document chunking with metadata attachment."""

import re
from datetime import datetime

from app.config import get_settings
from app.models.internal import Chunk, ChunkMetadata, Document
from app.observability import get_logger
from app.utils.hashing import hash_content

logger = get_logger(__name__)


class RecursiveChunker:
    """Recursively splits documents into chunks with overlap.

    Uses hierarchical separators to maintain semantic coherence:
    1. Double newlines (paragraphs)
    2. Single newlines
    3. Sentences (period + space)
    4. Words (space)
    """

    SEPARATORS = ["\n\n", "\n", ". ", " "]

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        embedding_model: str | None = None,
    ):
        """Initialize the chunker.

        Args:
            chunk_size: Target chunk size in tokens (uses config default)
            chunk_overlap: Overlap size in tokens (uses config default)
            embedding_model: Embedding model name for metadata
        """
        settings = get_settings()
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.embedding_model = embedding_model or settings.embedding_model
        # Rough estimate: 4 characters per token
        self.chars_per_token = 4

    def chunk_document(self, document: Document) -> list[Chunk]:
        """Split a document into chunks with metadata.

        Args:
            document: Document to chunk

        Returns:
            List of Chunk objects with attached metadata
        """
        if not document.content.strip():
            logger.warning("empty_document", doc_id=document.doc_id)
            return []

        # Split into text chunks
        text_chunks = self._split_text(
            document.content,
            max_chars=self.chunk_size * self.chars_per_token,
            overlap_chars=self.chunk_overlap * self.chars_per_token,
        )

        # Create Chunk objects with metadata
        chunks: list[Chunk] = []
        for idx, text in enumerate(text_chunks):
            metadata = ChunkMetadata(
                doc_id=document.doc_id,
                chunk_id=idx,
                file_path=document.file_path,
                content_hash=hash_content(text),
                embedding_model=self.embedding_model,
                embedding_version="2.2.2",  # sentence-transformers version
                created_at=datetime.utcnow(),
            )
            chunks.append(Chunk(content=text, metadata=metadata))

        logger.debug(
            "document_chunked",
            doc_id=document.doc_id,
            chunks=len(chunks),
            avg_size=sum(len(c.content) for c in chunks) // max(len(chunks), 1),
        )

        return chunks

    def _split_text(
        self,
        text: str,
        max_chars: int,
        overlap_chars: int,
        separator_idx: int = 0,
    ) -> list[str]:
        """Recursively split text using hierarchical separators.

        Args:
            text: Text to split
            max_chars: Maximum characters per chunk
            overlap_chars: Characters to overlap between chunks
            separator_idx: Current separator index in hierarchy

        Returns:
            List of text chunks
        """
        if len(text) <= max_chars:
            return [text.strip()] if text.strip() else []

        # Get current separator
        separator = self.SEPARATORS[separator_idx] if separator_idx < len(self.SEPARATORS) else " "

        # Split by current separator
        splits = text.split(separator)

        # If we can't split further, force split by character
        if len(splits) == 1:
            return self._force_split(text, max_chars, overlap_chars)

        # Merge splits into chunks of appropriate size
        chunks: list[str] = []
        current_chunk = ""

        for split in splits:
            # Add separator back (except for first split)
            piece = split if not current_chunk else separator + split

            if len(current_chunk) + len(piece) <= max_chars:
                current_chunk += piece
            else:
                # Current chunk is full
                if current_chunk.strip():
                    # Check if current chunk needs further splitting
                    if len(current_chunk) > max_chars and separator_idx < len(self.SEPARATORS) - 1:
                        chunks.extend(
                            self._split_text(
                                current_chunk, max_chars, overlap_chars, separator_idx + 1
                            )
                        )
                    else:
                        chunks.append(current_chunk.strip())

                # Start new chunk with overlap
                if overlap_chars > 0 and chunks:
                    overlap_text = chunks[-1][-overlap_chars:]
                    current_chunk = overlap_text + separator + split
                else:
                    current_chunk = split

        # Don't forget the last chunk
        if current_chunk.strip():
            if len(current_chunk) > max_chars and separator_idx < len(self.SEPARATORS) - 1:
                chunks.extend(
                    self._split_text(current_chunk, max_chars, overlap_chars, separator_idx + 1)
                )
            else:
                chunks.append(current_chunk.strip())

        return [c for c in chunks if c.strip()]

    def _force_split(self, text: str, max_chars: int, overlap_chars: int) -> list[str]:
        """Force split text by character when no separators work."""
        chunks: list[str] = []
        start = 0

        while start < len(text):
            end = min(start + max_chars, len(text))

            # Try to break at word boundary
            if end < len(text):
                space_idx = text.rfind(" ", start, end)
                if space_idx > start:
                    end = space_idx

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start with overlap
            start = end - overlap_chars if overlap_chars > 0 else end

        return chunks


def chunk_documents(documents: list[Document]) -> list[Chunk]:
    """Chunk multiple documents.

    Args:
        documents: List of documents to chunk

    Returns:
        List of all chunks from all documents
    """
    settings = get_settings()
    chunker = RecursiveChunker()
    all_chunks: list[Chunk] = []

    for doc in documents:
        chunks = chunker.chunk_document(doc)

        # Apply max chunks per doc limit
        if len(chunks) > settings.max_chunks_per_doc:
            logger.warning(
                "chunks_truncated",
                doc_id=doc.doc_id,
                original=len(chunks),
                truncated_to=settings.max_chunks_per_doc,
            )
            chunks = chunks[: settings.max_chunks_per_doc]

        all_chunks.extend(chunks)

    logger.info("chunking_completed", documents=len(documents), total_chunks=len(all_chunks))

    return all_chunks
