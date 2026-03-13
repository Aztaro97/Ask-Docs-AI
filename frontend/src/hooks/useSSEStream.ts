/**
 * Hook for managing SSE streaming state
 */

import { useCallback, useRef, useState } from 'react';
import { SSEClient } from '../services/sseClient';
import type { Citation, ErrorInfo, Message } from '../types';

interface UseSSEStreamOptions {
  baseUrl: string;
  onError?: (error: ErrorInfo) => void;
}

interface StreamMessageOptions {
  topK?: number;
  /**
   * If provided, called every time new streamed content/citations arrive.
   * Use this to update UI incrementally (ChatGPT-style streaming).
   */
  onMessage?: (message: Message) => void;
  /**
   * Optional message id to use for the streaming assistant message.
   * If omitted, a new id will be generated.
   */
  messageId?: string;
}

interface UseSSEStreamReturn {
  isStreaming: boolean;
  streamMessage: (question: string, options?: StreamMessageOptions) => Promise<Message>;
  cancelStream: () => void;
}

export function useSSEStream({ baseUrl, onError }: UseSSEStreamOptions): UseSSEStreamReturn {
  const [isStreaming, setIsStreaming] = useState(false);
  const clientRef = useRef<SSEClient | null>(null);
  const contentRef = useRef('');
  const citationsRef = useRef<Citation[]>([]);

  const streamMessage = useCallback(
    async (question: string, options?: StreamMessageOptions): Promise<Message> => {
      return new Promise((resolve, reject) => {
        if (!clientRef.current) {
          clientRef.current = new SSEClient(baseUrl);
        }

        contentRef.current = '';
        citationsRef.current = [];
        setIsStreaming(true);

        const messageId = options?.messageId ?? `msg-${Date.now()}`;
        let streamingMessage: Message = {
          id: messageId,
          role: 'assistant',
          content: '',
          timestamp: new Date(),
          isStreaming: true,
        };

        const updateMessage = () => {
          streamingMessage = {
            ...streamingMessage,
            content: contentRef.current,
            citations: citationsRef.current.length > 0 ? citationsRef.current : undefined,
          };
          options?.onMessage?.(streamingMessage);
        };

        clientRef.current.stream(question, options?.topK ?? 5, {
          onToken: (data) => {
            contentRef.current += data.content;
            updateMessage();
          },

          onCitation: (data) => {
            citationsRef.current = data.citations;
            updateMessage();
          },

          onDone: (_data) => {
            setIsStreaming(false);
            updateMessage();
            streamingMessage.isStreaming = false;
            resolve(streamingMessage);
          },

          onError: (data) => {
            setIsStreaming(false);
            const errorInfo: ErrorInfo = {
              type: data.type,
              message: data.message,
              retryable: data.retryable,
            };
            streamingMessage.error = errorInfo;
            onError?.(errorInfo);
            options?.onMessage?.(streamingMessage);
            resolve(streamingMessage);
          },

          onConnectionError: (error) => {
            setIsStreaming(false);
            const errorInfo: ErrorInfo = {
              type: 'network',
              message: error.message,
              retryable: true,
            };
            streamingMessage.error = errorInfo;
            onError?.(errorInfo);
            options?.onMessage?.(streamingMessage);
            reject(error);
          },
        });
      });
    },
    [baseUrl, onError]
  );

  const cancelStream = useCallback(() => {
    clientRef.current?.abort();
    setIsStreaming(false);
  }, []);

  return {
    isStreaming,
    streamMessage,
    cancelStream,
  };
}
