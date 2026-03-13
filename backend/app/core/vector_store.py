"""FAISS vector store for document embeddings."""

import json
import pickle
from pathlib import Path

import faiss
import numpy as np

from app.config import get_settings
from app.models.internal import Chunk, ChunkMetadata
from app.observability import get_logger, timed

logger = get_logger(__name__)


class VectorStore:
    """FAISS-based vector store with metadata management."""

    def __init__(self, dimension: int = 384, index_path: Path | None = None):
        """Initialize the vector store.

        Args:
            dimension: Embedding dimension (384 for all-MiniLM-L6-v2)
            index_path: Path to store index files
        """
        settings = get_settings()
        self.dimension = dimension
        self.index_path = index_path or settings.index_path
        self.index_path.mkdir(parents=True, exist_ok=True)

        # Initialize empty index
        self.index: faiss.IndexFlatL2 = faiss.IndexFlatL2(dimension)
        self.chunks: list[Chunk] = []
        self.metadata: list[ChunkMetadata] = []

        # Try to load existing index
        self._load_if_exists()

    @property
    def index_file(self) -> Path:
        return self.index_path / "index.faiss"

    @property
    def metadata_file(self) -> Path:
        return self.index_path / "metadata.pkl"

    @property
    def chunks_file(self) -> Path:
        return self.index_path / "chunks.pkl"

    def _load_if_exists(self) -> bool:
        """Load existing index if available."""
        if not self.index_file.exists():
            return False

        try:
            logger.info("loading_vector_store", path=str(self.index_path))
            self.index = faiss.read_index(str(self.index_file))

            with open(self.metadata_file, "rb") as f:
                self.metadata = pickle.load(f)

            with open(self.chunks_file, "rb") as f:
                self.chunks = pickle.load(f)

            logger.info("vector_store_loaded", vectors=self.index.ntotal)
            return True
        except Exception as e:
            logger.error("vector_store_load_failed", error=str(e))
            # Reset to empty state
            self.index = faiss.IndexFlatL2(self.dimension)
            self.chunks = []
            self.metadata = []
            return False

    def save(self) -> None:
        """Save index and metadata to disk."""
        logger.info("saving_vector_store", vectors=self.index.ntotal)

        faiss.write_index(self.index, str(self.index_file))

        with open(self.metadata_file, "wb") as f:
            pickle.dump(self.metadata, f)

        with open(self.chunks_file, "wb") as f:
            pickle.dump(self.chunks, f)

        logger.info("vector_store_saved")

    def add(self, chunks: list[Chunk], embeddings: np.ndarray) -> None:
        """Add chunks with their embeddings to the store.

        Args:
            chunks: List of Chunk objects
            embeddings: 2D numpy array of embeddings (n_chunks x dimension)
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Chunks and embeddings count mismatch: {len(chunks)} vs {len(embeddings)}"
            )

        # Ensure embeddings are float32 for FAISS
        embeddings = np.ascontiguousarray(embeddings.astype("float32"))

        # Add to FAISS index
        self.index.add(embeddings)

        # Store chunks and metadata
        self.chunks.extend(chunks)
        self.metadata.extend([c.metadata for c in chunks])

        logger.debug("vectors_added", count=len(chunks), total=self.index.ntotal)

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[tuple[Chunk, float]]:
        """Search for similar chunks.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return

        Returns:
            List of (Chunk, score) tuples, sorted by relevance
        """
        if self.index.ntotal == 0:
            logger.warning("search_empty_index")
            return []

        # Ensure proper shape and type
        query = np.ascontiguousarray(query_embedding.reshape(1, -1).astype("float32"))

        # Search
        k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(query, k)

        results: list[tuple[Chunk, float]] = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx >= 0 and idx < len(self.chunks):
                # Convert L2 distance to similarity score (0-1)
                # Lower distance = higher similarity
                score = 1 / (1 + dist)
                results.append((self.chunks[idx], score))

        logger.debug("search_completed", results=len(results), top_score=results[0][1] if results else 0)

        return results

    def clear(self) -> None:
        """Clear the index and metadata."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.chunks = []
        self.metadata = []
        logger.info("vector_store_cleared")

    def get_stats(self) -> dict:
        """Get index statistics."""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": type(self.index).__name__,
            "index_path": str(self.index_path),
        }


# Singleton instance
_vector_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    """Get the singleton vector store instance."""
    global _vector_store
    if _vector_store is None:
        from app.core.embeddings import get_embedding_model

        model = get_embedding_model()
        _vector_store = VectorStore(dimension=model.dimension)
    return _vector_store


@timed("vector_search")
async def search_similar(query_embedding: np.ndarray, top_k: int = 5) -> list[tuple[Chunk, float]]:
    """Search for similar chunks in the vector store.

    Args:
        query_embedding: Query embedding
        top_k: Number of results

    Returns:
        List of (Chunk, score) tuples
    """
    store = get_vector_store()
    return store.search(query_embedding, top_k)
