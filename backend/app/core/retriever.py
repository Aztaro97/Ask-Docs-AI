"""Document retriever combining vector search and reranking."""

import numpy as np

from app.config import get_settings
from app.core.embeddings import embed_query
from app.core.reranker import rerank_chunks
from app.core.vector_store import get_vector_store
from app.models.internal import RetrievedChunk
from app.observability import get_logger, timed

logger = get_logger(__name__)


class Retriever:
    """Retrieves relevant document chunks using vector search + reranking."""

    def __init__(self):
        """Initialize the retriever."""
        self.settings = get_settings()

    async def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        rerank: bool = True,
    ) -> list[RetrievedChunk]:
        """Retrieve relevant chunks for a query.

        Args:
            query: Query string
            top_k: Number of results to return
            rerank: Whether to apply cross-encoder reranking

        Returns:
            List of RetrievedChunk objects sorted by relevance
        """
        top_k = top_k or self.settings.top_k
        rerank_top_k = self.settings.rerank_top_k

        # Step 1: Embed the query
        query_embedding = await embed_query(query)

        # Step 2: Vector search (retrieve more if we're reranking)
        search_k = rerank_top_k if rerank else top_k
        store = get_vector_store()
        candidates = store.search(query_embedding, search_k)

        if not candidates:
            logger.warning("no_retrieval_results", query=query[:50])
            return []

        # Step 3: Rerank if enabled
        if rerank and len(candidates) > 0:
            results = await rerank_chunks(query, candidates, top_k)
        else:
            # Convert to RetrievedChunk without reranking
            results = [
                RetrievedChunk(chunk=chunk, score=score, rank=idx + 1)
                for idx, (chunk, score) in enumerate(candidates[:top_k])
            ]

        logger.info(
            "retrieval_completed",
            query_length=len(query),
            candidates=len(candidates),
            results=len(results),
            top_score=results[0].score if results else 0,
        )

        return results


# Singleton
_retriever: Retriever | None = None


def get_retriever() -> Retriever:
    """Get the singleton retriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


@timed("full_retrieval")
async def retrieve_documents(
    query: str,
    top_k: int | None = None,
    rerank: bool = True,
) -> list[RetrievedChunk]:
    """Retrieve relevant documents for a query.

    Args:
        query: Query string
        top_k: Number of results
        rerank: Apply reranking

    Returns:
        Retrieved chunks
    """
    retriever = get_retriever()
    return await retriever.retrieve(query, top_k, rerank)
