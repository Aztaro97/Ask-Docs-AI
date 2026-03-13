# API Reference

This document describes the Ask-Docs backend API endpoints.

## Query Endpoints

### POST /query/stream

Stream a RAG-based response to a question.

**Request Body:**
```json
{
  "question": "How do I get started?",
  "top_k": 5,
  "stream": true
}
```

**Parameters:**
- `question` (string, required): The user's question (1-500 characters)
- `top_k` (integer, optional): Number of documents to retrieve (1-20, default: 5)
- `stream` (boolean, optional): Whether to stream the response (default: true)

**Response:** Server-Sent Events (SSE) stream with the following event types:

1. `token`: Streamed response tokens
   ```json
   {"content": "Hello", "index": 0}
   ```

2. `citation`: Source citations
   ```json
   {"citations": [{"doc_id": "...", "snippet": "...", "score": 0.85}]}
   ```

3. `done`: Stream completion
   ```json
   {"total_tokens": 150, "retrieval_ms": 45.2, "generation_ms": 1200.5}
   ```

4. `error`: Error event
   ```json
   {"type": "model_error", "message": "...", "retryable": true}
   ```

### POST /query

Non-streaming query endpoint. Returns the full response at once.

**Request Body:** Same as `/query/stream`

**Response:**
```json
{
  "answer": "The full response text...",
  "citations": [...],
  "metadata": {
    "total_tokens": 150,
    "retrieval_ms": 45.2,
    "generation_ms": 1200.5
  }
}
```

## Index Endpoints

### POST /index

Index documents from the docs directory.

**Request Body:**
```json
{
  "path": "./docs",
  "force_reindex": false
}
```

**Response:**
```json
{
  "status": "success",
  "documents_indexed": 10,
  "chunks_created": 150
}
```

### GET /index/stats

Get index statistics.

**Response:**
```json
{
  "total_documents": 10,
  "total_chunks": 150,
  "embedding_model": "all-MiniLM-L6-v2",
  "last_indexed": "2024-01-15T10:30:00Z"
}
```

## Error Handling

All endpoints return errors in a consistent format:

```json
{
  "detail": {
    "type": "validation_error",
    "message": "Question must be between 1 and 500 characters",
    "retryable": false
  }
}
```

Error types:
- `validation_error`: Invalid request parameters
- `model_error`: LLM generation failed
- `retrieval_error`: Document retrieval failed
- `network_error`: Connection issues
- `rate_limit`: Too many requests
