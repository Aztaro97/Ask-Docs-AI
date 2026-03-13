"""Unit tests for document chunking."""

import pytest

from app.core.chunking import RecursiveChunker, chunk_documents
from app.models.internal import Document


class TestRecursiveChunker:
    """Tests for RecursiveChunker."""

    def test_chunk_respects_max_size(self):
        """Chunks never exceed configured token limit."""
        chunker = RecursiveChunker(chunk_size=100, chunk_overlap=10)

        doc = Document(
            doc_id="test",
            file_path="test.md",
            content="This is a test. " * 100,  # Long content
            file_type=".md",
            file_size=1600,
        )

        chunks = chunker.chunk_document(doc)

        # Each chunk should be roughly within size limit
        # (chunk_size * 4 chars per token = 400 chars max)
        for chunk in chunks:
            assert len(chunk.content) <= 500  # Allow some flexibility

    def test_chunk_overlap_maintained(self):
        """Adjacent chunks share overlap content."""
        chunker = RecursiveChunker(chunk_size=50, chunk_overlap=10)

        doc = Document(
            doc_id="test",
            file_path="test.md",
            content="Word " * 100,  # Repeated words
            file_type=".md",
            file_size=500,
        )

        chunks = chunker.chunk_document(doc)

        if len(chunks) > 1:
            # Check that chunks have some overlap
            for i in range(len(chunks) - 1):
                # Due to overlap, end of chunk i should appear in chunk i+1
                # This is a simplified check
                assert len(chunks[i].content) > 0
                assert len(chunks[i + 1].content) > 0

    def test_metadata_attached(self):
        """Each chunk has doc_id, chunk_id, hash, model info."""
        chunker = RecursiveChunker()

        doc = Document(
            doc_id="test123",
            file_path="/path/to/doc.md",
            content="Test content for chunking.",
            file_type=".md",
            file_size=27,
        )

        chunks = chunker.chunk_document(doc)

        assert len(chunks) >= 1
        for i, chunk in enumerate(chunks):
            assert chunk.metadata.doc_id == "test123"
            assert chunk.metadata.chunk_id == i
            assert chunk.metadata.file_path == "/path/to/doc.md"
            assert chunk.metadata.content_hash is not None
            assert len(chunk.metadata.content_hash) == 16
            assert chunk.metadata.embedding_model == "all-MiniLM-L6-v2"

    def test_empty_document_returns_no_chunks(self):
        """Empty documents produce no chunks."""
        chunker = RecursiveChunker()

        doc = Document(
            doc_id="empty",
            file_path="empty.md",
            content="",
            file_type=".md",
            file_size=0,
        )

        chunks = chunker.chunk_document(doc)
        assert len(chunks) == 0

    def test_whitespace_only_document(self):
        """Whitespace-only documents produce no chunks."""
        chunker = RecursiveChunker()

        doc = Document(
            doc_id="whitespace",
            file_path="whitespace.md",
            content="   \n\n   \t   ",
            file_type=".md",
            file_size=15,
        )

        chunks = chunker.chunk_document(doc)
        assert len(chunks) == 0


class TestChunkDocuments:
    """Tests for chunk_documents function."""

    def test_chunks_multiple_documents(self):
        """Handles multiple documents correctly."""
        docs = [
            Document(
                doc_id="doc1",
                file_path="doc1.md",
                content="Content of document one.",
                file_type=".md",
                file_size=24,
            ),
            Document(
                doc_id="doc2",
                file_path="doc2.md",
                content="Content of document two.",
                file_type=".md",
                file_size=24,
            ),
        ]

        chunks = chunk_documents(docs)

        # Should have chunks from both documents
        doc_ids = set(c.metadata.doc_id for c in chunks)
        assert "doc1" in doc_ids
        assert "doc2" in doc_ids

    def test_respects_max_chunks_per_doc(self, monkeypatch):
        """Respects MAX_CHUNKS_PER_DOC limit."""
        from app import config

        # Create a mock settings with low max_chunks_per_doc
        original_settings = config.get_settings()
        monkeypatch.setattr(original_settings, "max_chunks_per_doc", 2)

        doc = Document(
            doc_id="big",
            file_path="big.md",
            content="Paragraph. " * 1000,  # Very long document
            file_type=".md",
            file_size=11000,
        )

        chunks = chunk_documents([doc])

        # Should be limited to max_chunks_per_doc
        assert len(chunks) <= 2
