/**
 * Message list component with scroll area
 */

import { useEffect, useRef } from 'react';
import { BookOpen, MessageSquare } from 'lucide-react';
import { ScrollArea } from './ui/scroll-area';
import { Message } from './Message';
import type { Message as MessageType } from '../types';

interface MessageListProps {
  messages: MessageType[];
  onSuggestionClick?: (suggestion: string) => void;
  suggestions?: string[];
}

const DEFAULT_SUGGESTIONS = [
  'How do I get started?',
  'What are the key features?',
  'Show me the API reference',
];

export function MessageList({
  messages,
  onSuggestionClick,
  suggestions = DEFAULT_SUGGESTIONS
}: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      const scrollContainer = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
        <div className="relative">
          <div className="absolute inset-0 bg-primary/20 rounded-full blur-xl animate-pulse" />
          <div className="relative flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-primary/20 to-primary/5 border border-primary/20">
            <BookOpen className="w-7 h-7 text-primary" />
          </div>
        </div>
        <h3 className="mt-6 font-semibold text-foreground">Ask anything</h3>
        <p className="mt-2 text-sm text-muted-foreground max-w-[240px] leading-relaxed">
          Ask a question about the documentation to get started
        </p>
        <div className="mt-6 flex flex-col gap-2">
          {suggestions.map((suggestion, index) => (
            <SuggestionChip
              key={index}
              text={suggestion}
              onClick={() => onSuggestionClick?.(suggestion)}
            />
          ))}
        </div>
      </div>
    );
  }

  return (
    <ScrollArea className="flex-1" ref={scrollRef}>
      <div className="p-4 space-y-1">
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}
      </div>
    </ScrollArea>
  );
}

interface SuggestionChipProps {
  text: string;
  onClick?: () => void;
}

function SuggestionChip({ text, onClick }: SuggestionChipProps) {
  return (
    <button
      onClick={onClick}
      className="group flex items-center gap-2 px-4 py-2 rounded-full border border-border bg-background hover:bg-accent hover:border-primary/30 transition-all duration-200 cursor-pointer"
    >
      <MessageSquare className="w-3.5 h-3.5 text-muted-foreground group-hover:text-primary transition-colors" />
      <span className="text-sm text-muted-foreground group-hover:text-foreground transition-colors">
        {text}
      </span>
    </button>
  );
}
