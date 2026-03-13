import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock EventSource for SSE tests
class MockEventSource {
  url: string;
  readyState: number = 0;
  onopen: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSED = 2;

  constructor(url: string) {
    this.url = url;
    this.readyState = MockEventSource.CONNECTING;
    // Simulate connection after a tick
    setTimeout(() => {
      this.readyState = MockEventSource.OPEN;
      if (this.onopen) {
        this.onopen(new Event('open'));
      }
    }, 0);
  }

  close() {
    this.readyState = MockEventSource.CLOSED;
  }

  // Test helper to simulate events
  simulateMessage(data: string, event?: string) {
    if (this.onmessage) {
      const messageEvent = new MessageEvent(event || 'message', { data });
      this.onmessage(messageEvent);
    }
  }

  simulateError() {
    if (this.onerror) {
      this.onerror(new Event('error'));
    }
  }
}

// @ts-expect-error - Mocking global
global.EventSource = MockEventSource;

// Mock fetch for API tests
global.fetch = vi.fn();
