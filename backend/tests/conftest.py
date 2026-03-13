"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def temp_docs_dir():
    """Create a temporary directory with sample documents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        docs_path = Path(tmpdir)

        # Create sample markdown file
        (docs_path / "test.md").write_text(
            """# Test Document

This is a test document for unit testing.

## Section 1

This section contains information about testing.
Unit tests are important for code quality.

## Section 2

This section has more content.
The content is used to verify chunking works correctly.
"""
        )

        # Create sample text file
        (docs_path / "sample.txt").write_text(
            """Sample Text File

This is a plain text file for testing.
It contains multiple paragraphs.

Each paragraph should be handled properly by the parser.
"""
        )

        yield docs_path


@pytest.fixture
def sample_chunks():
    """Create sample chunks for testing."""
    from app.models.internal import Chunk, ChunkMetadata

    return [
        Chunk(
            content="This is the first chunk about testing.",
            metadata=ChunkMetadata(
                doc_id="doc1",
                chunk_id=0,
                file_path="test.md",
                content_hash="abc123",
                embedding_model="all-MiniLM-L6-v2",
                embedding_version="2.2.2",
            ),
        ),
        Chunk(
            content="This is the second chunk about documentation.",
            metadata=ChunkMetadata(
                doc_id="doc1",
                chunk_id=1,
                file_path="test.md",
                content_hash="def456",
                embedding_model="all-MiniLM-L6-v2",
                embedding_version="2.2.2",
            ),
        ),
    ]
