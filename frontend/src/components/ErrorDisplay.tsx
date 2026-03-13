/**
 * Error display component with user-friendly messages
 */

import { AlertCircle, WifiOff, Clock, Server, ShieldAlert, RefreshCw } from 'lucide-react';
import { Button } from './ui/button';
import { cn } from '../lib/utils';
import type { ErrorInfo, ErrorType } from '../types';

interface ErrorDisplayProps {
  error: ErrorInfo;
  onRetry?: () => void;
}

interface ErrorConfig {
  icon: typeof AlertCircle;
  title: string;
  description: string;
  iconClass: string;
}

const errorConfigs: Record<ErrorType, ErrorConfig> = {
  network: {
    icon: WifiOff,
    title: 'Connection Error',
    description: 'Unable to reach the server. Please check your connection.',
    iconClass: 'text-amber-500',
  },
  rate_limit: {
    icon: Clock,
    title: 'Rate Limited',
    description: 'Too many requests. Please wait a moment before trying again.',
    iconClass: 'text-amber-500',
  },
  model: {
    icon: Server,
    title: 'Model Error',
    description: 'The AI model encountered an issue processing your request.',
    iconClass: 'text-red-500',
  },
  retrieval: {
    icon: AlertCircle,
    title: 'Retrieval Error',
    description: 'Could not retrieve relevant documents for your query.',
    iconClass: 'text-red-500',
  },
  validation: {
    icon: ShieldAlert,
    title: 'Validation Error',
    description: 'Your request could not be validated. Please try rephrasing.',
    iconClass: 'text-amber-500',
  },
};

export function ErrorDisplay({ error, onRetry }: ErrorDisplayProps) {
  const config = errorConfigs[error.type] || errorConfigs.network;
  const Icon = config.icon;

  // Use error message if provided, otherwise use default description
  const description = error.message || config.description;

  return (
    <div className="flex items-start gap-3 p-3 rounded-lg bg-destructive/10 border border-destructive/20">
      <div className={cn('mt-0.5', config.iconClass)}>
        <Icon className="w-5 h-5" />
      </div>

      <div className="flex-1 min-w-0">
        <h4 className="text-sm font-semibold text-foreground">
          {config.title}
        </h4>
        <p className="mt-0.5 text-sm text-muted-foreground leading-relaxed">
          {description}
        </p>

        {error.retryable && onRetry && (
          <Button
            variant="outline"
            size="sm"
            onClick={onRetry}
            className="mt-2 h-7 text-xs"
          >
            <RefreshCw className="w-3 h-3 mr-1.5" />
            Try Again
          </Button>
        )}
      </div>
    </div>
  );
}
