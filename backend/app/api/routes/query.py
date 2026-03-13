"""Query endpoint with RAG and streaming."""

from fastapi import APIRouter, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings
from app.core.rag_pipeline import get_rag_pipeline
from app.core.streaming import create_sse_response
from app.models.requests import QueryRequest
from app.models.responses import ErrorResponse, ErrorType, QueryResponse
from app.observability import get_logger
from app.safety.validation import ValidationError, validate_query, validate_top_k

router = APIRouter()
logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=QueryResponse)
@limiter.limit("60/minute")
async def query_documents(request: Request, query_request: QueryRequest) -> QueryResponse:
    """Query the indexed documents.

    For streaming responses, set stream=true and use SSE endpoint.

    Args:
        request: FastAPI request (for rate limiting)
        query_request: QueryRequest with question and options

    Returns:
        QueryResponse with answer and citations (non-streaming)
        or SSE stream (if stream=true)
    """
    settings = get_settings()

    try:
        # Validate input
        question = validate_query(query_request.question)
        top_k = validate_top_k(query_request.top_k)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                type=ErrorType.VALIDATION_ERROR,
                message=e.message,
                retryable=False,
            ).model_dump(),
        )

    logger.info("query_received", question_length=len(question), stream=query_request.stream)

    # Handle streaming request
    if query_request.stream:
        return create_sse_response(question, top_k)

    # Non-streaming request
    try:
        pipeline = get_rag_pipeline()
        result = await pipeline.run(question, top_k=top_k)

        return QueryResponse(
            answer=result.answer,
            citations=result.citations,
            abstained=result.abstained,
            retrieval_ms=round(result.retrieval_ms, 2),
            generation_ms=round(result.generation_ms, 2),
            total_tokens=len(result.answer.split()),  # Rough estimate
        )

    except Exception as e:
        logger.error("query_failed", error=str(e))

        # Classify error
        error_type = ErrorType.MODEL_ERROR
        if "connection" in str(e).lower():
            error_type = ErrorType.NETWORK_ERROR
        elif "rate" in str(e).lower():
            error_type = ErrorType.RATE_LIMIT

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                type=error_type,
                message=str(e),
                retryable=error_type != ErrorType.RATE_LIMIT,
            ).model_dump(),
        )


@router.post("/stream")
@limiter.limit("60/minute")
async def query_stream(request: Request, query_request: QueryRequest):
    """Stream query response via SSE.

    This endpoint always streams, regardless of the stream parameter.

    Args:
        request: FastAPI request
        query_request: QueryRequest

    Returns:
        SSE EventSourceResponse with token stream
    """
    try:
        question = validate_query(query_request.question)
        top_k = validate_top_k(query_request.top_k)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                type=ErrorType.VALIDATION_ERROR,
                message=e.message,
                retryable=False,
            ).model_dump(),
        )

    logger.info("stream_query_received", question_length=len(question))

    return create_sse_response(question, top_k)
