"""Embedding model wrapper with caching."""

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import get_settings
from app.models.internal import Chunk
from app.observability import get_logger, timed

logger = get_logger(__name__)


class EmbeddingModel:
    """Wrapper for sentence-transformers embedding model with batching."""

    _instance: "EmbeddingModel | None" = None

    def __init__(self, model_name: str | None = None):
        """Initialize the embedding model.

        Args:
            model_name: Model name to load. Uses config default if not provided.
        """
        settings = get_settings()
        self.model_name = model_name or settings.embedding_model
        self.batch_size = settings.embedding_batch_size

        logger.info("loading_embedding_model", model=self.model_name)
        self.model = SentenceTransformer(self.model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(
            "embedding_model_loaded",
            model=self.model_name,
            dimension=self.dimension,
        )

    @classmethod
    def get_instance(cls) -> "EmbeddingModel":
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single text string.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as numpy array
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding  # type: ignore

    def embed_texts(self, texts: list[str]) -> np.ndarray:
        """Embed multiple texts with batching.

        Args:
            texts: List of texts to embed

        Returns:
            2D numpy array of embeddings (n_texts x dimension)
        """
        if not texts:
            return np.array([])

        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=len(texts) > 100,
            convert_to_numpy=True,
        )
        return embeddings  # type: ignore

    def embed_chunks(self, chunks: list[Chunk]) -> np.ndarray:
        """Embed a list of chunks.

        Args:
            chunks: List of Chunk objects

        Returns:
            2D numpy array of embeddings
        """
        texts = [chunk.content for chunk in chunks]
        return self.embed_texts(texts)


@lru_cache(maxsize=1)
def get_embedding_model() -> EmbeddingModel:
    """Get the singleton embedding model instance."""
    return EmbeddingModel.get_instance()


@timed("embedding")
async def embed_query(query: str) -> np.ndarray:
    """Embed a query string.

    Args:
        query: Query text

    Returns:
        Query embedding vector
    """
    model = get_embedding_model()
    return model.embed_text(query)


@timed("batch_embedding")
async def embed_chunks(chunks: list[Chunk]) -> np.ndarray:
    """Embed multiple chunks.

    Args:
        chunks: List of chunks to embed

    Returns:
        2D numpy array of embeddings
    """
    model = get_embedding_model()
    return model.embed_chunks(chunks)
