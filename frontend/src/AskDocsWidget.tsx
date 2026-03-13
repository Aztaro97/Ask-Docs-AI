/**
 * Main Ask-Docs Widget Component
 *
 * Embeddable RAG-based Q&A widget for documentation.
 *
 * @example
 * ```tsx
 * import { AskDocsWidget } from 'ask-docs-widget';
 * import 'ask-docs-widget/styles';
 *
 * function App() {
 *   return <AskDocsWidget baseUrl="http://localhost:8000" />;
 * }
 * ```
 */

import { useCallback, useState } from 'react';
import { ChatInput } from './components/ChatInput';
import { MessageList } from './components/MessageList';
import { StatusBadge } from './components/StatusBadge';
import { TokenBudget } from './components/TokenBudget';
import { useSSEStream } from './hooks/useSSEStream';
import './styles/widget.css';
import type { ErrorInfo, Message, WidgetConfig } from './types';

export interface AskDocsWidgetProps extends Partial<WidgetConfig> {
  /** Backend API URL (required) */
  baseUrl: string;
  /** Custom class name for styling */
  className?: string;
  /** Show token budget indicator */
  showTokenBudget?: boolean;
  /** Show connection status */
  showStatus?: boolean;
}

export function AskDocsWidget({
  baseUrl,
  placeholder = 'Ask a question about the documentation...',
  maxTokenBudget = 10000,
  className = '',
  showTokenBudget = true,
  showStatus = false,
}: AskDocsWidgetProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [tokenCount, setTokenCount] = useState(0);
  const [lastError, setLastError] = useState<ErrorInfo | null>(null);

  const handleError = useCallback((error: ErrorInfo) => {
    setLastError(error);
  }, []);

  const { isStreaming, streamMessage } = useSSEStream({
    baseUrl,
    onError: handleError,
  });

  const handleSubmit = useCallback(
    async (question: string) => {
      // Clear last error
      setLastError(null);

      // Add user message
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: question,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);

      // Add placeholder assistant message
      const assistantId = `assistant-${Date.now()}`;
      const placeholderMessage: Message = {
        id: assistantId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
        isStreaming: true,
      };
      setMessages((prev) => [...prev, placeholderMessage]);

      try {
        const response = await streamMessage(question, {
          messageId: assistantId,
          onMessage: (partial) => {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantId
                  ? {
                      ...msg,
                      content: partial.content,
                      citations: partial.citations,
                      error: partial.error,
                      isStreaming: true,
                    }
                  : msg
              )
            );
          },
        });

        // Update the placeholder with the final response
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantId
              ? {
                  ...msg,
                  content: response.content,
                  citations: response.citations,
                  error: response.error,
                  isStreaming: false,
                }
              : msg
          )
        );

        // Update token count (rough estimate)
        setTokenCount((prev) => prev + question.length / 4 + response.content.length / 4);
      } catch (error) {
        // Update message with error
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantId
              ? {
                  ...msg,
                  error: {
                    type: 'network',
                    message: (error as Error).message,
                    retryable: true,
                  },
                  isStreaming: false,
                }
              : msg
          )
        );
      }
    },
    [streamMessage]
  );

  return (
    <div className={`ask-docs-widget ${className}`}>
      {showStatus && (
        <div className="ask-docs-header">
          <StatusBadge
            status={isStreaming ? 'loading' : lastError ? 'error' : 'connected'}
            message={isStreaming ? 'Generating...' : undefined}
          />
        </div>
      )}

      <MessageList messages={messages} />

      <div className="ask-docs-footer">
        {showTokenBudget && (
          <TokenBudget used={Math.round(tokenCount)} max={maxTokenBudget} />
        )}
        <ChatInput
          onSubmit={handleSubmit}
          disabled={isStreaming}
          placeholder={placeholder}
        />
      </div>
    </div>
  );
}

export default AskDocsWidget;
