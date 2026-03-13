/**
 * Message component for chat display
 */

import type { Message as MessageType } from '../types';
import { CitationList } from './Citation';
import { ErrorDisplay } from './ErrorDisplay';

interface MessageProps {
  message: MessageType;
}

export function Message({ message }: MessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`ask-docs-message ${isUser ? 'user' : 'assistant'}`}>
      <div className="ask-docs-message-avatar">
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="ask-docs-message-content">
        {message.error ? (
          <ErrorDisplay error={message.error} />
        ) : (
          <>
            <div className="ask-docs-message-text">
              {message.content}
              {message.isStreaming && (
                <span className="ask-docs-cursor">▊</span>
              )}
            </div>
            {!message.isStreaming && message.citations && (
              <CitationList citations={message.citations} />
            )}
          </>
        )}
        <div className="ask-docs-message-time">
          {formatTime(message.timestamp)}
        </div>
      </div>
    </div>
  );
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
  });
}
