/**
 * Message list component
 */

import { useEffect, useRef } from 'react';
import type { Message as MessageType } from '../types';
import { Message } from './Message';

interface MessageListProps {
  messages: MessageType[];
}

export function MessageList({ messages }: MessageListProps) {
  const listRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="ask-docs-empty">
        <div className="ask-docs-empty-icon">📚</div>
        <p>Ask a question about the documentation to get started.</p>
      </div>
    );
  }

  return (
    <div className="ask-docs-messages" ref={listRef}>
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
    </div>
  );
}
