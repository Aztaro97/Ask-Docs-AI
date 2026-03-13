# Configuration Guide

This guide explains how to configure the Ask-Docs system.

## Environment Variables

Configure the backend using environment variables:

### Core Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCS_PATH` | `./docs` | Path to documentation files |
| `INDEX_PATH` | `./data/index` | Path to store the vector index |
| `TOP_K` | `5` | Default number of documents to retrieve |
| `MIN_RELEVANCE_SCORE` | `0.5` | Minimum score for document relevance |

### Embedding Model

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `EMBEDDING_DIMENSION` | `384` | Embedding vector dimension |

### LLM Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `ollama` | LLM provider (ollama or llama-cpp) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2:3b` | Ollama model to use |
| `MAX_TOKENS` | `1024` | Maximum response tokens |
| `TEMPERATURE` | `0.7` | Generation temperature |

### Chunking Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `CHUNK_SIZE` | `512` | Tokens per chunk |
| `CHUNK_OVERLAP` | `64` | Overlap between chunks |
| `MAX_CHUNKS_PER_DOC` | `1000` | Maximum chunks per document |

## Widget Configuration

Configure the frontend widget with props:

```tsx
<AskDocsWidget
  baseUrl="http://localhost:8000"
  placeholder="Ask me anything..."
  maxTokenBudget={10000}
  showTokenBudget={true}
  showStatus={true}
  defaultTheme="system"
  showThemeToggle={true}
/>
```

### Available Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `baseUrl` | string | required | Backend API URL |
| `placeholder` | string | "Ask a question..." | Input placeholder |
| `maxTokenBudget` | number | 10000 | Max token budget display |
| `showTokenBudget` | boolean | true | Show token usage |
| `showStatus` | boolean | false | Show connection status |
| `defaultTheme` | string | "system" | Theme: light/dark/system |
| `showThemeToggle` | boolean | true | Show theme toggle button |

## Theming

The widget supports custom theming via CSS variables:

```css
.ask-docs-widget {
  --primary: 238 84% 67%;
  --background: 0 0% 100%;
  --foreground: 222 47% 11%;
  --muted: 210 40% 96%;
  --border: 214 32% 91%;
}

.ask-docs-widget.dark {
  --background: 222 47% 11%;
  --foreground: 210 40% 98%;
  --muted: 217 33% 17%;
  --border: 217 33% 17%;
}
```

## Security Considerations

- Always use HTTPS in production
- Set appropriate CORS headers
- Enable rate limiting for API endpoints
- Sanitize user input to prevent injection attacks
- Never expose sensitive information in responses
