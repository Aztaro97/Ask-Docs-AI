/**
 * Error display component
 */

import type { ErrorInfo } from '../types';
import { classifyError } from '../utils/errorClassifier';

interface ErrorDisplayProps {
  error: ErrorInfo;
  onRetry?: () => void;
}

export function ErrorDisplay({ error, onRetry }: ErrorDisplayProps) {
  const display = classifyError(error);

  return (
    <div className="ask-docs-error">
      <div className="ask-docs-error-icon">{display.icon}</div>
      <div className="ask-docs-error-content">
        <h4 className="ask-docs-error-title">{display.title}</h4>
        <p className="ask-docs-error-description">{display.description}</p>
        {display.actionLabel && onRetry && (
          <button className="ask-docs-error-action" onClick={onRetry}>
            {display.actionLabel}
          </button>
        )}
      </div>
    </div>
  );
}
