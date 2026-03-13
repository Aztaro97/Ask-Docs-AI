/**
 * Chat input component with submit button
 */

import { KeyboardEvent, useCallback, useState } from 'react';

interface ChatInputProps {
  onSubmit: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

export function ChatInput({
  onSubmit,
  disabled = false,
  placeholder = 'Ask a question about the documentation...',
  maxLength = 500,
}: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSubmit = useCallback(() => {
    const trimmed = input.trim();
    if (trimmed && !disabled) {
      onSubmit(trimmed);
      setInput('');
    }
  }, [input, disabled, onSubmit]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="ask-docs-input-container">
      <textarea
        className="ask-docs-input"
        value={input}
        onChange={(e) => setInput(e.target.value.slice(0, maxLength))}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={2}
        aria-label="Question input"
      />
      <div className="ask-docs-input-footer">
        <span className="ask-docs-char-count">
          {input.length}/{maxLength}
        </span>
        <button
          className="ask-docs-submit-btn"
          onClick={handleSubmit}
          disabled={disabled || !input.trim()}
          aria-label="Submit question"
        >
          {disabled ? (
            <span className="ask-docs-spinner" />
          ) : (
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path d="M22 2L11 13" />
              <path d="M22 2L15 22L11 13L2 9L22 2Z" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}
