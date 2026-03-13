/**
 * API client for Ask-Docs backend
 */

import type { QueryRequest } from '../types';

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  async query(request: QueryRequest): Promise<Response> {
    const response = await fetch(`${this.baseUrl}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: request.question,
        top_k: request.top_k ?? 5,
        stream: request.stream ?? true,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(error.detail?.message || error.message || 'Request failed');
    }

    return response;
  }

  createStreamUrl(_question: string, _topK: number = 5): string {
    return `${this.baseUrl}/query/stream`;
  }

  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}
