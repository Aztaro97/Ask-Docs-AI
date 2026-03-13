"""SSE streaming for token-by-token response generation."""

import json
import time
from collections.abc import AsyncGenerator
from typing import Any

from sse_starlette.sse import EventSourceResponse

from app.config import get_settings
from app.core.llm import get_llm
from app.core.rag_pipeline import build_rag_prompt, extract_citations
from app.core.retriever import retrieve_documents
from app.models.internal import RetrievedChunk
from app.models.responses import CitationResponse, ErrorType
from app.observability import get_logger
from app.safety.abstention import get_abstention_response, should_abstain
from app.safety.redaction import redact_content

logger = get_logger(__name__)


async def stream_rag_response(
    query: str,
    top_k: int | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """Stream RAG response as SSE events.

    Yields events in format:
    - event: token, data: {"content": "...", "index": n}
    - event: citation, data: {"citations": [...]}
    - event: done, data: {"total_tokens": n, "retrieval_ms": n, "generation_ms": n}
    - event: error, data: {"type": "...", "message": "...", "retryable": bool}

    Args:
        query: User question
        top_k: Number of chunks to retrieve

    Yields:
        SSE event dictionaries
    """
    settings = get_settings()
    top_k = top_k or settings.top_k

    retrieval_start = time.perf_counter()
    total_tokens = 0
    chunks: list[RetrievedChunk] = []

    try:
        # Redact PII
        query = redact_content(query)

        # Retrieve
        chunks = await retrieve_documents(query, top_k=top_k, rerank=True)
        retrieval_ms = (time.perf_counter() - retrieval_start) * 1000

        # Check abstention
        should_abs, reason = should_abstain(chunks)
        if should_abs:
            abstention_msg = get_abstention_response()
            # Stream abstention message as tokens
            for i, word in enumerate(abstention_msg.split()):
                yield {
                    "event": "token",
                    "data": json.dumps({"content": word + " ", "index": i}),
                }
                total_tokens += 1

            yield {
                "event": "done",
                "data": json.dumps(
                    {
                        "total_tokens": total_tokens,
                        "retrieval_ms": round(retrieval_ms, 2),
                        "generation_ms": 0,
                        "abstained": True,
                    }
                ),
            }
            return

        # Build prompt
        prompt = build_rag_prompt(query, chunks)

        # Stream generation
        generation_start = time.perf_counter()
        llm = await get_llm()
        full_response = ""

        async for token in llm.generate_stream(prompt):
            full_response += token
            yield {
                "event": "token",
                "data": json.dumps({"content": token, "index": total_tokens}),
            }
            total_tokens += 1

        generation_ms = (time.perf_counter() - generation_start) * 1000

        # Extract and send citations
        citations = extract_citations(full_response, chunks)
        yield {
            "event": "citation",
            "data": json.dumps(
                {"citations": [c.model_dump() for c in citations]}
            ),
        }

        # Send completion event
        yield {
            "event": "done",
            "data": json.dumps(
                {
                    "total_tokens": total_tokens,
                    "retrieval_ms": round(retrieval_ms, 2),
                    "generation_ms": round(generation_ms, 2),
                    "abstained": False,
                }
            ),
        }

        logger.info(
            "stream_completed",
            tokens=total_tokens,
            citations=len(citations),
            retrieval_ms=round(retrieval_ms, 2),
            generation_ms=round(generation_ms, 2),
        )

    except Exception as e:
        logger.error("stream_error", error=str(e))

        # Determine error type
        error_type = ErrorType.MODEL_ERROR
        retryable = True

        if "connection" in str(e).lower():
            error_type = ErrorType.NETWORK_ERROR
        elif "rate" in str(e).lower():
            error_type = ErrorType.RATE_LIMIT
            retryable = False

        yield {
            "event": "error",
            "data": json.dumps(
                {
                    "type": error_type.value,
                    "message": str(e),
                    "retryable": retryable,
                }
            ),
        }


def create_sse_response(
    query: str,
    top_k: int | None = None,
) -> EventSourceResponse:
    """Create an SSE response for streaming RAG.

    Args:
        query: User question
        top_k: Number of chunks to retrieve

    Returns:
        FastAPI EventSourceResponse
    """

    async def event_generator():
        async for event in stream_rag_response(query, top_k):
            yield event

    return EventSourceResponse(
        event_generator(),
        media_type="text/event-stream",
    )
