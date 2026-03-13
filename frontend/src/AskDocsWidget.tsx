/**
 * Main Ask-Docs Widget Component
 *
 * Embeddable RAG-based Q&A widget for documentation.
 * Features dark mode, modern UI with shadcn/ui components.
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

import { Moon, Sparkles, Sun } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';
import { ChatInput } from './components/ChatInput';
import { MessageList } from './components/MessageList';
import { StatusBadge } from './components/StatusBadge';
import { TokenBudget } from './components/TokenBudget';
import { Button } from './components/ui/button';
import { TooltipProvider } from './components/ui/tooltip';
import { useSSEStream } from './hooks/useSSEStream';
import { cn } from './lib/utils';
import './styles/globals.css';
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
  /** Default theme */
  defaultTheme?: 'light' | 'dark' | 'system';
  /** Show theme toggle */
  showThemeToggle?: boolean;
  /** Custom suggestion prompts shown when no messages */
  suggestions?: string[];
}

export function AskDocsWidget({
  baseUrl,
  placeholder = 'Ask a question about the documentation...',
  maxTokenBudget = 10000,
  className = '',
  showTokenBudget = true,
  showStatus = false,
  defaultTheme = 'system',
  showThemeToggle = true,
  suggestions,
}: AskDocsWidgetProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [tokenCount, setTokenCount] = useState(0);
  const [lastError, setLastError] = useState<ErrorInfo | null>(null);
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    if (defaultTheme === 'system') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return defaultTheme;
  });

  // Listen for system theme changes
  useEffect(() => {
    if (defaultTheme !== 'system') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      setTheme(e.matches ? 'dark' : 'light');
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [defaultTheme]);

  const toggleTheme = useCallback(() => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  }, []);

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
    <TooltipProvider>
      <div
        className={cn(
          'flex flex-col h-[700px] max-h-[85vh] min-h-[400px] bg-background border border-border rounded-2xl shadow-lg overflow-hidden transition-colors duration-200',
          theme === 'dark' && 'dark',
          className
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-muted/30">
          <div className="flex items-center gap-2">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-primary/10">
              <Sparkles className="w-4 h-4 text-primary" />
            </div>
            <span className="font-semibold text-sm text-foreground">Ask Docs</span>
          </div>

          <div className="flex items-center gap-2">
            {showStatus && (
              <StatusBadge
                status={isStreaming ? 'loading' : lastError ? 'error' : 'connected'}
                message={isStreaming ? 'Generating...' : undefined}
              />
            )}

            {showThemeToggle && (
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleTheme}
                className="h-8 w-8"
                aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
              >
                {theme === 'light' ? (
                  <Moon className="h-4 w-4" />
                ) : (
                  <Sun className="h-4 w-4" />
                )}
              </Button>
            )}
          </div>
        </div>

        {/* Messages Area */}
        <MessageList
          messages={messages}
          suggestions={suggestions}
          onSuggestionClick={handleSubmit}
        />

        {/* Footer */}
        <div className="p-4 border-t border-border bg-background">
          {showTokenBudget && tokenCount > 0 && (
            <TokenBudget used={Math.round(tokenCount)} max={maxTokenBudget} />
          )}
          <ChatInput
            onSubmit={handleSubmit}
            disabled={isStreaming}
            placeholder={placeholder}
          />
        </div>
      </div>
    </TooltipProvider>
  );
}

export default AskDocsWidget;
