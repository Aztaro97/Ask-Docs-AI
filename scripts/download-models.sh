#!/bin/bash
# Download required models for Ask-Docs

set -e

echo "=== Downloading Embedding Model ==="
python -c "
from sentence_transformers import SentenceTransformer
print('Downloading all-MiniLM-L6-v2...')
model = SentenceTransformer('all-MiniLM-L6-v2')
print('Embedding model downloaded!')
"

echo ""
echo "=== Downloading Reranker Model ==="
python -c "
from sentence_transformers import CrossEncoder
print('Downloading ms-marco-MiniLM-L-6-v2...')
model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
print('Reranker model downloaded!')
"

echo ""
echo "=== Pulling Ollama Model ==="
if command -v ollama &> /dev/null; then
    echo "Pulling llama3.2:3b (this may take a while)..."
    ollama pull llama3.2:3b
    echo "Ollama model pulled!"
else
    echo "Ollama not found. Please install Ollama first:"
    echo "  curl -fsSL https://ollama.com/install.sh | sh"
    echo "Then run: ollama pull llama3.2:3b"
fi

echo ""
echo "=== Done! ==="
