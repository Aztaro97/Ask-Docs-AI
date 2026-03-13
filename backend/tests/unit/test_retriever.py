"""Unit tests for document retrieval."""

import numpy as np
import pytest

from app.models.internal import Chunk, ChunkMetadata, RetrievedChunk


class TestRetrievedChunk:
    """Tests for RetrievedChunk model."""

    def test_retrieval_results_structure(self, sample_chunks):
        """Verify RetrievedChunk has correct structure."""
        chunk = sample_chunks[0]
        retrieved = RetrievedChunk(chunk=chunk, score=0.85, rank=1)

        assert retrieved.score == 0.85
        assert retrieved.rank == 1
        assert retrieved.content == chunk.content
        assert retrieved.metadata.doc_id == chunk.metadata.doc_id

    def test_retrieval_scores_valid_range(self, sample_chunks):
        """Scores should be in valid range."""
        chunk = sample_chunks[0]

        # Valid score
        retrieved = RetrievedChunk(chunk=chunk, score=0.5, rank=1)
        assert 0 <= retrieved.score <= 1

        # Edge cases
        retrieved_zero = RetrievedChunk(chunk=chunk, score=0.0, rank=1)
        assert retrieved_zero.score == 0.0

        retrieved_one = RetrievedChunk(chunk=chunk, score=1.0, rank=1)
        assert retrieved_one.score == 1.0


class TestAbstention:
    """Tests for abstention logic."""

    def test_abstention_on_no_chunks(self):
        """Abstains when no chunks are retrieved."""
        from app.safety.abstention import should_abstain

        result, reason = should_abstain([])
        assert result is True
        assert "No relevant documents" in reason

    def test_abstention_on_low_scores(self, sample_chunks):
        """Abstains when scores are too low."""
        from app.safety.abstention import should_abstain

        # Create low-scoring results
        low_score_results = [
            RetrievedChunk(chunk=sample_chunks[0], score=0.3, rank=1),
            RetrievedChunk(chunk=sample_chunks[1], score=0.2, rank=2),
        ]

        result, reason = should_abstain(low_score_results)
        assert result is True
        assert "below threshold" in reason.lower() or "insufficient" in reason.lower()

    def test_no_abstention_on_good_scores(self, sample_chunks):
        """Does not abstain when scores are good."""
        from app.safety.abstention import should_abstain

        # Create high-scoring results
        good_results = [
            RetrievedChunk(chunk=sample_chunks[0], score=0.85, rank=1),
            RetrievedChunk(chunk=sample_chunks[1], score=0.75, rank=2),
        ]

        result, reason = should_abstain(good_results)
        assert result is False
        assert reason == ""


class TestVectorStore:
    """Tests for vector store operations."""

    def test_vector_store_add_and_search(self, sample_chunks, tmp_path):
        """Vector store can add and search vectors."""
        from app.core.vector_store import VectorStore

        # Create store with temp path
        store = VectorStore(dimension=384, index_path=tmp_path)

        # Create fake embeddings
        embeddings = np.random.rand(2, 384).astype("float32")

        # Add chunks
        store.add(sample_chunks, embeddings)

        assert store.index.ntotal == 2

        # Search
        query_embedding = np.random.rand(384).astype("float32")
        results = store.search(query_embedding, top_k=2)

        assert len(results) == 2
        assert all(isinstance(r[0], Chunk) for r in results)
        assert all(isinstance(r[1], float) for r in results)

    def test_vector_store_save_and_load(self, sample_chunks, tmp_path):
        """Vector store can save and load index."""
        from app.core.vector_store import VectorStore

        # Create and populate store
        store = VectorStore(dimension=384, index_path=tmp_path)
        embeddings = np.random.rand(2, 384).astype("float32")
        store.add(sample_chunks, embeddings)
        store.save()

        # Create new store and verify it loads
        new_store = VectorStore(dimension=384, index_path=tmp_path)

        assert new_store.index.ntotal == 2
        assert len(new_store.chunks) == 2

    def test_vector_store_clear(self, sample_chunks, tmp_path):
        """Vector store can clear all data."""
        from app.core.vector_store import VectorStore

        store = VectorStore(dimension=384, index_path=tmp_path)
        embeddings = np.random.rand(2, 384).astype("float32")
        store.add(sample_chunks, embeddings)

        assert store.index.ntotal == 2

        store.clear()

        assert store.index.ntotal == 0
        assert len(store.chunks) == 0
