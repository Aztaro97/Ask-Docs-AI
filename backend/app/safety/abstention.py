"""Abstention logic for low-confidence responses."""

from app.config import get_settings
from app.models.internal import RetrievedChunk
from app.observability import get_logger

logger = get_logger(__name__)

ABSTENTION_MESSAGE = (
    "I don't have enough information in the documentation to answer this question "
    "confidently. Please try rephrasing your question or check if the topic is "
    "covered in the indexed documents."
)


def should_abstain(chunks: list[RetrievedChunk]) -> tuple[bool, str]:
    """Determine if the system should abstain from answering.

    Abstention triggers:
    1. Fewer than min_citations chunks with score > min_relevance_score
    2. Top chunk score is below min_relevance_score
    3. No chunks retrieved

    Args:
        chunks: Retrieved and reranked chunks

    Returns:
        Tuple of (should_abstain, reason)
    """
    settings = get_settings()

    # No chunks retrieved
    if not chunks:
        logger.info("abstention_triggered", reason="no_chunks")
        return True, "No relevant documents found"

    # Check top score
    top_score = chunks[0].score
    if top_score < settings.min_relevance_score:
        logger.info(
            "abstention_triggered",
            reason="low_top_score",
            top_score=top_score,
            threshold=settings.min_relevance_score,
        )
        return True, f"Top relevance score ({top_score:.2f}) below threshold"

    # Count high-confidence chunks
    high_confidence_count = sum(
        1 for chunk in chunks if chunk.score >= settings.min_relevance_score
    )

    if high_confidence_count < settings.min_citations:
        logger.info(
            "abstention_triggered",
            reason="insufficient_citations",
            count=high_confidence_count,
            required=settings.min_citations,
        )
        return True, f"Only {high_confidence_count} confident sources found"

    return False, ""


def get_abstention_response() -> str:
    """Get the standard abstention response message."""
    return ABSTENTION_MESSAGE
