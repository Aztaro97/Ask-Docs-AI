/**
 * Status badge component for connection state
 */


type Status = 'connected' | 'disconnected' | 'loading' | 'error';

interface StatusBadgeProps {
  status: Status;
  message?: string;
}

export function StatusBadge({ status, message }: StatusBadgeProps) {
  const statusConfig = {
    connected: { color: 'green', label: 'Connected', icon: '●' },
    disconnected: { color: 'gray', label: 'Disconnected', icon: '○' },
    loading: { color: 'blue', label: 'Loading...', icon: '◐' },
    error: { color: 'red', label: 'Error', icon: '✕' },
  };

  const config = statusConfig[status];

  return (
    <div className={`ask-docs-status ask-docs-status-${config.color}`}>
      <span className="ask-docs-status-icon">{config.icon}</span>
      <span className="ask-docs-status-label">{message || config.label}</span>
    </div>
  );
}
