"""Cross-encoder reranker for improving retrieval quality."""

from functools import lru_cache

from sentence_transformers import CrossEncoder

from app.config import get_settings
from app.models.internal import Chunk, RetrievedChunk
from app.observability import get_logger, timed

logger = get_logger(__name__)


class Reranker:
    """Cross-encoder reranker using ms-marco-MiniLM model."""

    _instance: "Reranker | None" = None

    def __init__(self, model_name: str | None = None):
        """Initialize the reranker.

        Args:
            model_name: Model name to load. Uses config default if not provided.
        """
        settings = get_settings()
        self.model_name = model_name or settings.reranker_model

        logger.info("loading_reranker_model", model=self.model_name)
        self.model = CrossEncoder(self.model_name, max_length=512)
        logger.info("reranker_model_loaded", model=self.model_name)

    @classmethod
    def get_instance(cls) -> "Reranker":
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def rerank(
        self,
        query: str,
        chunks: list[tuple[Chunk, float]],
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        """Rerank chunks based on relevance to query.

        Args:
            query: Query string
            chunks: List of (Chunk, initial_score) tuples from retrieval
            top_k: Number of top results to return (None = all)

        Returns:
            List of RetrievedChunk objects sorted by reranked score
        """
        if not chunks:
            return []

        settings = get_settings()
        top_k = top_k or settings.top_k

        # Prepare pairs for cross-encoder
        pairs = [(query, chunk.content) for chunk, _ in chunks]

        # Get reranker scores
        scores = self.model.predict(pairs, show_progress_bar=False)

        # Combine with chunks
        ranked: list[tuple[Chunk, float]] = list(zip([c for c, _ in chunks], scores))

        # Sort by score descending
        ranked.sort(key=lambda x: x[1], reverse=True)

        # Take top_k and convert to RetrievedChunk
        results: list[RetrievedChunk] = []
        for rank, (chunk, score) in enumerate(ranked[:top_k]):
            # Normalize score to 0-1 range using sigmoid
            normalized_score = 1 / (1 + 2.718 ** (-score))
            results.append(
                RetrievedChunk(
                    chunk=chunk,
                    score=normalized_score,
                    rank=rank + 1,
                )
            )

        logger.debug(
            "reranking_completed",
            input_count=len(chunks),
            output_count=len(results),
            top_score=results[0].score if results else 0,
        )

        return results


@lru_cache(maxsize=1)
def get_reranker() -> Reranker:
    """Get the singleton reranker instance."""
    return Reranker.get_instance()


@timed("reranking")
async def rerank_chunks(
    query: str,
    chunks: list[tuple[Chunk, float]],
    top_k: int | None = None,
) -> list[RetrievedChunk]:
    """Rerank retrieved chunks using cross-encoder.

    Args:
        query: Query string
        chunks: Retrieved chunks with scores
        top_k: Number of results to return

    Returns:
        Reranked chunks as RetrievedChunk objects
    """
    reranker = get_reranker()
    return reranker.rerank(query, chunks, top_k)
