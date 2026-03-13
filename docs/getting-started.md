# Getting Started with Ask-Docs

Welcome to Ask-Docs! This guide will help you get up and running quickly.

## Overview

Ask-Docs is a RAG-based Q&A system that lets you ask questions about your documentation and get accurate, cited answers.

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Ollama (for local LLM)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/example/ask-docs
   cd ask-docs
   ```

2. Run the setup script:
   ```bash
   ./scripts/setup-dev.sh
   ```

3. Start the services:
   ```bash
   make docker-up
   ```

4. Open http://localhost:5173 in your browser.

## Using the Widget

The Ask-Docs widget provides a simple chat interface:

1. **Ask a Question**: Type your question in the input box
2. **View Response**: The AI will stream its response with inline citations
3. **Explore Sources**: Click on citations to see the source text

## Indexing Documents

To index your own documents:

```bash
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{"path": "./docs", "force_reindex": true}'
```

Supported formats:
- Markdown (.md)
- Plain text (.txt)
- HTML (.html)
- PDF (.pdf)
- Excel (.xlsx)

## Next Steps

- Read the [API Reference](./api-reference.md) for endpoint documentation
- Check the [Configuration Guide](./configuration-guide.txt) for customization options
- See the [FAQ](./faq.html) for common questions
