/**
 * Chat input component with auto-resize textarea and submit button
 */

import { KeyboardEvent, useCallback, useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { Button } from './ui/button';
import { cn } from '../lib/utils';

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
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    // Reset height to auto to get the correct scrollHeight
    textarea.style.height = 'auto';
    // Set height to scrollHeight, capped at max height
    const maxHeight = 120;
    textarea.style.height = `${Math.min(textarea.scrollHeight, maxHeight)}px`;
  }, [input]);

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

  const charCountStatus = (() => {
    const ratio = input.length / maxLength;
    if (ratio >= 1) return 'at-limit';
    if (ratio >= 0.8) return 'near-limit';
    return 'normal';
  })();

  return (
    <div className="relative">
      <div className={cn(
        'flex flex-col rounded-xl border-2 bg-muted/30 transition-all duration-200',
        'focus-within:border-primary focus-within:ring-2 focus-within:ring-primary/20',
        disabled && 'opacity-60'
      )}>
        {/* Textarea */}
        <textarea
          ref={textareaRef}
          className={cn(
            'w-full px-4 py-3 text-sm bg-transparent resize-none',
            'placeholder:text-muted-foreground text-foreground',
            'focus:outline-none',
            'min-h-[44px] max-h-[120px]'
          )}
          value={input}
          onChange={(e) => setInput(e.target.value.slice(0, maxLength))}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          aria-label="Question input"
        />

        {/* Footer */}
        <div className="flex items-center justify-between px-3 py-2 border-t border-border/50">
          <div className="flex items-center gap-2">
            <span
              className={cn(
                'text-[11px] font-medium tabular-nums transition-colors',
                charCountStatus === 'normal' && 'text-muted-foreground',
                charCountStatus === 'near-limit' && 'text-amber-500',
                charCountStatus === 'at-limit' && 'text-destructive'
              )}
            >
              {input.length}/{maxLength}
            </span>
            {!disabled && (
              <span className="text-[10px] text-muted-foreground hidden sm:inline">
                Press Enter to send
              </span>
            )}
          </div>

          <Button
            size="icon"
            onClick={handleSubmit}
            disabled={disabled || !input.trim()}
            className={cn(
              'h-8 w-8 rounded-lg transition-all',
              input.trim() && !disabled && 'bg-primary hover:bg-primary/90'
            )}
            aria-label="Submit question"
          >
            {disabled ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
