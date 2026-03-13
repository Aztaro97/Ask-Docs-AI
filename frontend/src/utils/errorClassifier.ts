/**
 * Error classification utilities
 */

import type { ErrorInfo, ErrorType } from '../types';

interface ErrorDisplay {
  title: string;
  description: string;
  icon: string;
  actionLabel?: string;
}

export function classifyError(error: ErrorInfo): ErrorDisplay {
  switch (error.type) {
    case 'model':
      return {
        title: 'Model Error',
        description: 'The AI model encountered an issue while generating a response.',
        icon: '🤖',
        actionLabel: error.retryable ? 'Try Again' : undefined,
      };

    case 'retrieval':
      return {
        title: 'No Results Found',
        description: 'Could not find relevant information in the documentation.',
        icon: '🔍',
        actionLabel: 'Rephrase Question',
      };

    case 'network':
      return {
        title: 'Connection Error',
        description: 'Unable to connect to the server. Please check your connection.',
        icon: '🌐',
        actionLabel: 'Retry',
      };

    case 'rate_limit':
      return {
        title: 'Rate Limited',
        description: 'Too many requests. Please wait a moment before trying again.',
        icon: '⏱️',
      };

    case 'validation':
      return {
        title: 'Invalid Input',
        description: error.message || 'Please check your input and try again.',
        icon: '⚠️',
      };

    default:
      return {
        title: 'Error',
        description: error.message || 'An unexpected error occurred.',
        icon: '❌',
        actionLabel: error.retryable ? 'Retry' : undefined,
      };
  }
}

export function isModelError(type: ErrorType): boolean {
  return type === 'model';
}

export function isRetrievalError(type: ErrorType): boolean {
  return type === 'retrieval';
}

export function isNetworkError(type: ErrorType): boolean {
  return type === 'network';
}
