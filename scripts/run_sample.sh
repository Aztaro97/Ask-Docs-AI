#!/bin/bash
# run_sample.sh - One-liner to index sample docs and run a test query
# Usage: ./scripts/run_sample.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

echo "=== Ask-Docs Sample Runner ==="
echo "Backend URL: $BACKEND_URL"
echo ""

# Check if backend is running
echo "1. Checking backend health..."
if ! curl -s "$BACKEND_URL/health" > /dev/null 2>&1; then
    echo "ERROR: Backend is not running at $BACKEND_URL"
    echo "Start it with: make backend (or make dev)"
    exit 1
fi
echo "   Backend is healthy"
echo ""

# Index documents
echo "2. Indexing documents from ./docs..."
INDEX_RESPONSE=$(curl -s -X POST "$BACKEND_URL/index" \
    -H "Content-Type: application/json" \
    -d '{"force_reindex": false}')

echo "   Index response: $INDEX_RESPONSE"
echo ""

# Run sample query
echo "3. Running sample query..."
QUERY_RESPONSE=$(curl -s -X POST "$BACKEND_URL/query" \
    -H "Content-Type: application/json" \
    -d '{"question": "What is this project about?", "top_k": 3}')

echo "   Query response:"
echo "$QUERY_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$QUERY_RESPONSE"
echo ""

# Test streaming endpoint
echo "4. Testing streaming endpoint (first 5 events)..."
timeout 10 curl -s -N -X POST "$BACKEND_URL/query/stream" \
    -H "Content-Type: application/json" \
    -H "Accept: text/event-stream" \
    -d '{"question": "Summarize the main features", "top_k": 3}' 2>/dev/null | head -20 || true
echo ""
echo ""

echo "=== Sample run complete ==="
echo "Open http://localhost:5173 (dev) or http://localhost:5173 (docker) to use the widget"
