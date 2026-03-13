# Ask-Docs API Reference

Complete API documentation for the Ask-Docs backend.

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health Check

#### GET /health

Check if the service is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

#### GET /health/ready

Check if the service is ready to accept requests.

**Response:**
```json
{
  "status": "ready",
  "models_loaded": true,
  "config_valid": true
}
```

### Document Indexing

#### POST /index

Index documents from a directory.

**Request Body:**
```json
{
  "path": "./docs",
  "force_reindex": false
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| path | string | ./docs | Path to documents directory |
| force_reindex | boolean | false | Force re-indexing of all documents |

**Response:**
```json
{
  "status": "completed",
  "documents_indexed": 5,
  "chunks_created": 42,
  "duration_ms": 1234.56,
  "errors": []
}
```

### Querying

#### POST /query

Query the indexed documents.

**Request Body:**
```json
{
  "question": "How do I get started?",
  "top_k": 5,
  "stream": true
}
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| question | string | required | The question to answer |
| top_k | integer | 5 | Number of chunks to retrieve |
| stream | boolean | true | Enable SSE streaming |

**Non-Streaming Response:**
```json
{
  "answer": "To get started, you need to...",
  "citations": [
    {
      "id": 1,
      "doc_id": "abc123",
      "chunk_id": 0,
      "file_path": "./docs/getting-started.md",
      "snippet": "Getting Started with Ask-Docs...",
      "score": 0.89
    }
  ],
  "abstained": false,
  "retrieval_ms": 45.2,
  "generation_ms": 2100.5,
  "total_tokens": 150
}
```

**Streaming Response (SSE):**
```
event: token
data: {"content": "To", "index": 0}

event: token
data: {"content": " get", "index": 1}

event: citation
data: {"citations": [...]}

event: done
data: {"total_tokens": 150, "retrieval_ms": 45.2, "generation_ms": 2100.5}
```

## Error Codes

| Code | Type | Description |
|------|------|-------------|
| 400 | validation | Invalid request parameters |
| 404 | not_found | Resource not found |
| 429 | rate_limit | Too many requests |
| 500 | model | LLM generation error |
| 503 | retrieval | No relevant documents found |

## Rate Limiting

The API is rate limited to 60 requests per minute per IP address.

## CORS

CORS is enabled for all origins in development. Configure appropriately for production.
