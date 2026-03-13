/**
 * SSE Client for streaming responses
 */

import type { CitationData, DoneData, ErrorData, TokenData } from '../types';

export interface SSECallbacks {
  onToken: (data: TokenData) => void;
  onCitation: (data: CitationData) => void;
  onDone: (data: DoneData) => void;
  onError: (data: ErrorData) => void;
  onConnectionError: (error: Error) => void;
}

export class SSEClient {
  private baseUrl: string;
  private abortController: AbortController | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  async stream(
    question: string,
    topK: number,
    callbacks: SSECallbacks
  ): Promise<void> {
    // Abort any existing connection
    this.abort();

    this.abortController = new AbortController();

    try {
      const response = await fetch(`${this.baseUrl}/query/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({
          question,
          top_k: topK,
          stream: true,
        }),
        signal: this.abortController.signal,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ message: 'Unknown error' }));
        throw new Error(error.detail?.message || error.message || 'Stream failed');
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';
      // These must persist across network chunks: SSE frames can be split across reads.
      let currentEvent = '';
      let currentData = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (let line of lines) {
          // Strip carriage return from Windows-style line endings
          line = line.replace(/\r$/, '');

          if (line.startsWith('event:')) {
            currentEvent = line.slice(6).trim();
          } else if (line.startsWith('data:')) {
            const dataLine = line.slice(5).trimStart();
            // SSE allows multiple data lines; join with newline (spec).
            currentData = currentData ? `${currentData}\n${dataLine}` : dataLine;
          } else if (line === '') {
            // Empty line ends the event frame. Dispatch if we have data.
            if (currentData) {
              const eventName = currentEvent || 'message';
              this.handleEvent(eventName, currentData, callbacks);
            }
            currentEvent = '';
            currentData = '';
          }
        }
      }
    } catch (error) {
      if ((error as Error).name === 'AbortError') {
        return; // Stream was intentionally aborted
      }
      callbacks.onConnectionError(error as Error);
    }
  }

  private handleEvent(event: string, data: string, callbacks: SSECallbacks): void {
    try {
      const parsed = JSON.parse(data);

      switch (event) {
        case 'token':
          callbacks.onToken(parsed as TokenData);
          break;
        case 'citation':
          callbacks.onCitation(parsed as CitationData);
          break;
        case 'done':
          callbacks.onDone(parsed as DoneData);
          break;
        case 'error':
          callbacks.onError(parsed as ErrorData);
          break;
        default:
          console.warn('Unknown SSE event type:', event, data);
      }
    } catch (e) {
      console.error('Failed to parse SSE data:', e, 'Raw data:', data);
    }
  }

  abort(): void {
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
  }
}
