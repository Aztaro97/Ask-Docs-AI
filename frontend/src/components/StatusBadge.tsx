/**
 * Status badge component for connection status
 */

import { cn } from '../lib/utils';

type StatusType = 'connected' | 'loading' | 'error' | 'disconnected';

interface StatusBadgeProps {
  status: StatusType;
  message?: string;
}

const statusConfig: Record<StatusType, { label: string; color: string; dotClass: string }> = {
  connected: {
    label: 'Connected',
    color: 'text-emerald-600 dark:text-emerald-400',
    dotClass: 'bg-emerald-500 shadow-emerald-500/50',
  },
  loading: {
    label: 'Loading',
    color: 'text-blue-600 dark:text-blue-400',
    dotClass: 'bg-blue-500 shadow-blue-500/50 animate-pulse',
  },
  error: {
    label: 'Error',
    color: 'text-red-600 dark:text-red-400',
    dotClass: 'bg-red-500 shadow-red-500/50',
  },
  disconnected: {
    label: 'Disconnected',
    color: 'text-muted-foreground',
    dotClass: 'bg-muted-foreground',
  },
};

export function StatusBadge({ status, message }: StatusBadgeProps) {
  const config = statusConfig[status];
  const displayText = message || config.label;

  return (
    <div
      className={cn(
        'inline-flex items-center gap-2 px-3 py-1.5 rounded-full',
        'bg-background border border-border',
        'text-xs font-medium',
        config.color
      )}
    >
      <span
        className={cn(
          'w-2 h-2 rounded-full shadow-sm',
          config.dotClass
        )}
        aria-hidden="true"
      />
      <span>{displayText}</span>
    </div>
  );
}
