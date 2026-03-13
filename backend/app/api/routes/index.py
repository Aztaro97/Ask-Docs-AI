"""Document indexing endpoint."""

import time
from pathlib import Path

from fastapi import APIRouter, HTTPException, status

from app.config import get_settings
from app.core.chunking import chunk_documents
from app.core.embeddings import get_embedding_model
from app.core.vector_store import get_vector_store
from app.ingestion.loader import DocumentLoader
from app.models.requests import IndexRequest
from app.models.responses import IndexResponse
from app.observability import get_logger, timed

router = APIRouter()
logger = get_logger(__name__)


@router.post("", response_model=IndexResponse)
@timed("indexing")
async def index_documents(request: IndexRequest) -> IndexResponse:
    """Index documents from a directory.

    Loads documents, chunks them, generates embeddings, and builds the vector index.

    Args:
        request: IndexRequest with optional path and force_reindex flag

    Returns:
        IndexResponse with statistics about the indexing operation
    """
    start_time = time.perf_counter()
    settings = get_settings()

    # Determine docs path
    docs_path = Path(request.path) if request.path else settings.docs_path

    if not docs_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documents path not found: {docs_path}",
        )

    logger.info("indexing_started", path=str(docs_path), force=request.force_reindex)

    # Get vector store
    store = get_vector_store()

    # Clear existing index if force reindex
    if request.force_reindex:
        store.clear()
        logger.info("existing_index_cleared")

    # Load documents
    loader = DocumentLoader(docs_path)
    documents = loader.load_all()

    if not documents:
        return IndexResponse(
            status="completed",
            documents_indexed=0,
            chunks_created=0,
            duration_ms=round((time.perf_counter() - start_time) * 1000, 2),
            errors=["No documents found in the specified path"],
        )

    # Chunk documents
    chunks = chunk_documents(documents)

    if not chunks:
        return IndexResponse(
            status="completed",
            documents_indexed=len(documents),
            chunks_created=0,
            duration_ms=round((time.perf_counter() - start_time) * 1000, 2),
            errors=["Documents found but no chunks created"],
        )

    # Generate embeddings
    logger.info("generating_embeddings", chunks=len(chunks))
    embedding_model = get_embedding_model()
    embeddings = embedding_model.embed_chunks(chunks)

    # Add to vector store
    store.add(chunks, embeddings)

    # Save index
    store.save()

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    logger.info(
        "indexing_completed",
        documents=len(documents),
        chunks=len(chunks),
        duration_ms=duration_ms,
    )

    return IndexResponse(
        status="completed",
        documents_indexed=len(documents),
        chunks_created=len(chunks),
        duration_ms=duration_ms,
        errors=loader.errors,
    )


@router.get("/stats")
async def get_index_stats() -> dict:
    """Get current index statistics."""
    store = get_vector_store()
    return store.get_stats()
