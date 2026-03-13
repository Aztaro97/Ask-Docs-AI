/**
 * Token budget component showing usage progress
 */

import { cn } from '../lib/utils';

interface TokenBudgetProps {
  used: number;
  max: number;
}

export function TokenBudget({ used, max }: TokenBudgetProps) {
  const percentage = Math.min((used / max) * 100, 100);
  const remaining = max - used;

  // Determine status
  const status = percentage >= 90 ? 'critical' : percentage >= 70 ? 'warning' : 'normal';

  const statusColors = {
    normal: 'bg-primary',
    warning: 'bg-amber-500',
    critical: 'bg-destructive',
  };

  const statusTextColors = {
    normal: 'text-muted-foreground',
    warning: 'text-amber-600 dark:text-amber-400',
    critical: 'text-destructive',
  };

  return (
    <div className="mb-3">
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-[11px] font-medium text-muted-foreground">
          Token Budget
        </span>
        <span className={cn('text-[11px] font-medium tabular-nums', statusTextColors[status])}>
          {used.toLocaleString()} / {max.toLocaleString()}
          {status !== 'normal' && (
            <span className="ml-1">
              ({remaining.toLocaleString()} left)
            </span>
          )}
        </span>
      </div>

      <div className="h-1.5 w-full bg-muted rounded-full overflow-hidden">
        <div
          className={cn(
            'h-full rounded-full transition-all duration-500 ease-out',
            statusColors[status]
          )}
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={used}
          aria-valuemin={0}
          aria-valuemax={max}
          aria-label={`Token usage: ${used} of ${max}`}
        />
      </div>
    </div>
  );
}
