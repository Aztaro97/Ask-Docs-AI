"""RAG pipeline orchestrating retrieval and generation."""

import re
from dataclasses import dataclass
from typing import Any

from app.config import get_settings
from app.core.llm import get_llm
from app.core.retriever import retrieve_documents
from app.models.internal import RetrievedChunk
from app.models.responses import CitationResponse
from app.observability import get_logger, timed
from app.safety.abstention import get_abstention_response, should_abstain
from app.safety.redaction import redact_content

logger = get_logger(__name__)


@dataclass
class RAGResult:
    """Result from RAG pipeline."""

    answer: str
    citations: list[CitationResponse]
    abstained: bool
    retrieval_ms: float
    generation_ms: float
    chunks_retrieved: int


def build_rag_prompt(query: str, chunks: list[RetrievedChunk]) -> str:
    """Build the prompt for RAG generation.

    Args:
        query: User query
        chunks: Retrieved chunks

    Returns:
        Formatted prompt string
    """
    # Build context from chunks
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        snippet = chunk.content[:500]  # Limit snippet length
        context_parts.append(f"[Source {i}]\n{snippet}")

    context = "\n\n".join(context_parts)

    prompt = f"""You are a helpful assistant that answers questions based on the provided documentation.
Use ONLY the information from the sources below to answer the question.
Include citation numbers [1], [2], etc. when using information from specific sources.
If the sources don't contain enough information to answer, say so clearly.

SOURCES:
{context}

QUESTION: {query}

ANSWER (with inline citations):"""

    return prompt


def extract_citations(
    answer: str,
    chunks: list[RetrievedChunk],
) -> list[CitationResponse]:
    """Extract citations from the generated answer.

    Args:
        answer: Generated answer text
        chunks: Retrieved chunks

    Returns:
        List of CitationResponse objects
    """
    # Find citation markers [1], [2], etc.
    citation_pattern = r"\[(\d+)\]"
    cited_numbers = set(int(m) for m in re.findall(citation_pattern, answer))

    citations: list[CitationResponse] = []
    for i, chunk in enumerate(chunks, 1):
        if i in cited_numbers or i <= 2:  # Always include top 2
            citations.append(
                CitationResponse(
                    id=i,
                    doc_id=chunk.metadata.doc_id,
                    chunk_id=chunk.metadata.chunk_id,
                    file_path=chunk.metadata.file_path,
                    snippet=chunk.content[:300],  # Truncate for response
                    score=chunk.score,
                )
            )

    return citations


class RAGPipeline:
    """RAG pipeline for question answering."""

    def __init__(self):
        """Initialize the pipeline."""
        self.settings = get_settings()

    @timed("rag_pipeline")
    async def run(
        self,
        query: str,
        top_k: int | None = None,
    ) -> RAGResult:
        """Run the full RAG pipeline.

        Args:
            query: User question
            top_k: Number of chunks to retrieve

        Returns:
            RAGResult with answer and citations
        """
        import time

        top_k = top_k or self.settings.top_k

        # Step 1: Redact PII from query
        query = redact_content(query)

        # Step 2: Retrieve relevant chunks
        retrieval_start = time.perf_counter()
        chunks = await retrieve_documents(query, top_k=top_k, rerank=True)
        retrieval_ms = (time.perf_counter() - retrieval_start) * 1000

        # Step 3: Check abstention
        should_abs, reason = should_abstain(chunks)
        if should_abs:
            return RAGResult(
                answer=get_abstention_response(),
                citations=[],
                abstained=True,
                retrieval_ms=retrieval_ms,
                generation_ms=0,
                chunks_retrieved=len(chunks),
            )

        # Step 4: Build prompt and generate
        prompt = build_rag_prompt(query, chunks)

        generation_start = time.perf_counter()
        llm = await get_llm()
        answer = await llm.generate(prompt)
        generation_ms = (time.perf_counter() - generation_start) * 1000

        # Step 5: Extract citations
        citations = extract_citations(answer, chunks)

        # Ensure minimum citations
        if len(citations) < self.settings.min_citations:
            # Add more from top chunks
            for i, chunk in enumerate(chunks[: self.settings.min_citations], 1):
                if not any(c.id == i for c in citations):
                    citations.append(
                        CitationResponse(
                            id=i,
                            doc_id=chunk.metadata.doc_id,
                            chunk_id=chunk.metadata.chunk_id,
                            file_path=chunk.metadata.file_path,
                            snippet=chunk.content[:300],
                            score=chunk.score,
                        )
                    )

        logger.info(
            "rag_completed",
            query_length=len(query),
            chunks=len(chunks),
            citations=len(citations),
            retrieval_ms=round(retrieval_ms, 2),
            generation_ms=round(generation_ms, 2),
        )

        return RAGResult(
            answer=answer,
            citations=sorted(citations, key=lambda c: c.id),
            abstained=False,
            retrieval_ms=retrieval_ms,
            generation_ms=generation_ms,
            chunks_retrieved=len(chunks),
        )


# Singleton
_pipeline: RAGPipeline | None = None


def get_rag_pipeline() -> RAGPipeline:
    """Get the singleton RAG pipeline."""
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline
