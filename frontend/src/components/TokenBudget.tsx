/**
 * Token budget indicator component
 */


interface TokenBudgetProps {
  used: number;
  max: number;
}

export function TokenBudget({ used, max }: TokenBudgetProps) {
  const percentage = Math.min((used / max) * 100, 100);
  const isWarning = percentage > 70;
  const isCritical = percentage > 90;

  return (
    <div className="ask-docs-token-budget">
      <div className="ask-docs-token-label">
        <span>Token Budget</span>
        <span>
          ~{used.toLocaleString()} / {max.toLocaleString()}
        </span>
      </div>
      <div className="ask-docs-token-bar">
        <div
          className={`ask-docs-token-fill ${isCritical ? 'critical' : isWarning ? 'warning' : ''}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
