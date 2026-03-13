# Getting Started with Ask-Docs

Welcome to Ask-Docs, an AI-powered documentation assistant that helps you find answers quickly.

## Quick Start

1. **Installation**: Install the widget using npm:
   ```bash
   npm install ask-docs-widget
   ```

2. **Basic Usage**: Import and use the widget in your React application:
   ```tsx
   import { AskDocsWidget } from 'ask-docs-widget';
   import 'ask-docs-widget/styles';

   function App() {
     return <AskDocsWidget baseUrl="http://localhost:8000" />;
   }
   ```

3. **Configuration**: You can customize the widget with various props:
   - `baseUrl`: The backend API URL (required)
   - `placeholder`: Custom input placeholder text
   - `maxTokenBudget`: Maximum token budget for responses
   - `showTokenBudget`: Show/hide token usage indicator
   - `defaultTheme`: Set default theme ('light', 'dark', or 'system')

## Features

- **Real-time Streaming**: Responses stream token-by-token for instant feedback
- **Dark Mode**: Built-in dark mode with system preference detection
- **Citations**: Every answer includes source citations
- **Copy to Clipboard**: Easily copy responses with one click
- **Responsive Design**: Works on desktop and mobile devices

## Requirements

- React 18 or higher
- A running backend server with the RAG API
- Node.js 18 or higher
