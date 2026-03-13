/**
 * Types for Ask-Docs Widget
 */

export interface Citation {
  id: number;
  doc_id: string;
  chunk_id: number;
  file_path: string;
  snippet: string;
  score: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: Date;
  isStreaming?: boolean;
  error?: ErrorInfo;
}

export interface ErrorInfo {
  type: ErrorType;
  message: string;
  retryable: boolean;
}

export type ErrorType = 'model' | 'retrieval' | 'network' | 'rate_limit' | 'validation';

export interface StreamEvent {
  event: 'token' | 'citation' | 'done' | 'error';
  data: TokenData | CitationData | DoneData | ErrorData;
}

export interface TokenData {
  content: string;
  index: number;
}

export interface CitationData {
  citations: Citation[];
}

export interface DoneData {
  total_tokens: number;
  retrieval_ms: number;
  generation_ms: number;
  abstained?: boolean;
}

export interface ErrorData {
  type: ErrorType;
  message: string;
  retryable: boolean;
}

export interface QueryRequest {
  question: string;
  top_k?: number;
  stream?: boolean;
}

export interface WidgetConfig {
  baseUrl: string;
  placeholder?: string;
  maxTokenBudget?: number;
  theme?: 'light' | 'dark' | 'auto';
}
