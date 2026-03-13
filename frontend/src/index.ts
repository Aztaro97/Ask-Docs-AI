/**
 * Ask-Docs Widget - Entry Point
 *
 * @packageDocumentation
 */

export { AskDocsWidget } from './AskDocsWidget';
export type { AskDocsWidgetProps } from './AskDocsWidget';
export type {
  Citation,
  Message,
  ErrorInfo,
  ErrorType,
  WidgetConfig,
  QueryRequest,
  StreamEvent,
} from './types';
export { useSSEStream } from './hooks/useSSEStream';
export { SSEClient } from './services/sseClient';
export { ApiClient } from './services/api';
