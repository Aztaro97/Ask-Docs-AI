import { describe, it, expect } from 'vitest';
import {
  classifyError,
  isModelError,
  isRetrievalError,
  isNetworkError,
} from './errorClassifier';
import type { ErrorInfo } from '../types';

describe('classifyError', () => {
  it('classifies model errors correctly', () => {
    const error: ErrorInfo = {
      type: 'model',
      message: 'Model failed',
      retryable: true,
    };

    const result = classifyError(error);

    expect(result.title).toBe('Model Error');
    expect(result.icon).toBe('🤖');
    expect(result.actionLabel).toBe('Try Again');
  });

  it('classifies non-retryable model errors without action', () => {
    const error: ErrorInfo = {
      type: 'model',
      message: 'Model failed',
      retryable: false,
    };

    const result = classifyError(error);
    expect(result.actionLabel).toBeUndefined();
  });

  it('classifies retrieval errors correctly', () => {
    const error: ErrorInfo = {
      type: 'retrieval',
      message: 'No docs found',
      retryable: true,
    };

    const result = classifyError(error);

    expect(result.title).toBe('No Results Found');
    expect(result.icon).toBe('🔍');
    expect(result.actionLabel).toBe('Rephrase Question');
  });

  it('classifies network errors correctly', () => {
    const error: ErrorInfo = {
      type: 'network',
      message: 'Connection failed',
      retryable: true,
    };

    const result = classifyError(error);

    expect(result.title).toBe('Connection Error');
    expect(result.icon).toBe('🌐');
    expect(result.actionLabel).toBe('Retry');
  });

  it('classifies rate limit errors correctly', () => {
    const error: ErrorInfo = {
      type: 'rate_limit',
      message: 'Too many requests',
      retryable: false,
    };

    const result = classifyError(error);

    expect(result.title).toBe('Rate Limited');
    expect(result.icon).toBe('⏱️');
    expect(result.actionLabel).toBeUndefined();
  });

  it('classifies validation errors correctly', () => {
    const error: ErrorInfo = {
      type: 'validation',
      message: 'Query too long',
      retryable: false,
    };

    const result = classifyError(error);

    expect(result.title).toBe('Invalid Input');
    expect(result.description).toBe('Query too long');
    expect(result.icon).toBe('⚠️');
  });

  it('uses default description for validation without message', () => {
    const error: ErrorInfo = {
      type: 'validation',
      message: '',
      retryable: false,
    };

    const result = classifyError(error);
    expect(result.description).toBe('Please check your input and try again.');
  });
});

describe('error type helpers', () => {
  it('isModelError returns true for model type', () => {
    expect(isModelError('model')).toBe(true);
    expect(isModelError('retrieval')).toBe(false);
    expect(isModelError('network')).toBe(false);
  });

  it('isRetrievalError returns true for retrieval type', () => {
    expect(isRetrievalError('retrieval')).toBe(true);
    expect(isRetrievalError('model')).toBe(false);
    expect(isRetrievalError('network')).toBe(false);
  });

  it('isNetworkError returns true for network type', () => {
    expect(isNetworkError('network')).toBe(true);
    expect(isNetworkError('model')).toBe(false);
    expect(isNetworkError('retrieval')).toBe(false);
  });
});
