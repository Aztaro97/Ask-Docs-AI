/**
 * Message component for chat display with copy functionality
 */

import { useState, useCallback } from 'react';
import { Copy, Check, User, Bot } from 'lucide-react';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Button } from './ui/button';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';
import { Skeleton } from './ui/skeleton';
import { CitationList } from './Citation';
import { ErrorDisplay } from './ErrorDisplay';
import { cn } from '../lib/utils';
import type { Message as MessageType } from '../types';

interface MessageProps {
  message: MessageType;
}

export function Message({ message }: MessageProps) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  const handleCopy = useCallback(async () => {
    if (!message.content) return;

    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [message.content]);

  return (
    <div
      className={cn(
        'group flex gap-3 py-4 animate-slide-in',
        isUser && 'flex-row-reverse'
      )}
    >
      {/* Avatar */}
      <Avatar className={cn(
        'h-8 w-8 shrink-0 border',
        isUser ? 'bg-primary border-primary' : 'bg-muted border-border'
      )}>
        <AvatarFallback className={cn(
          isUser ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
        )}>
          {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
        </AvatarFallback>
      </Avatar>

      {/* Content */}
      <div className={cn(
        'flex flex-col max-w-[75%] min-w-0',
        isUser && 'items-end'
      )}>
        {/* Message Bubble */}
        <div
          className={cn(
            'relative px-4 py-3 rounded-2xl text-sm leading-relaxed',
            isUser
              ? 'bg-primary text-primary-foreground rounded-br-md'
              : 'bg-muted text-foreground rounded-bl-md'
          )}
        >
          {message.error ? (
            <ErrorDisplay error={message.error} />
          ) : message.isStreaming && !message.content ? (
            <LoadingSkeleton />
          ) : (
            <>
              <div className="whitespace-pre-wrap break-words">
                {message.content}
                {message.isStreaming && (
                  <span className="inline-block w-0.5 h-4 ml-0.5 bg-current animate-blink align-text-bottom" />
                )}
              </div>
            </>
          )}
        </div>

        {/* Citations - only for assistant messages */}
        {isAssistant && !message.isStreaming && message.citations && message.citations.length > 0 && (
          <div className="mt-3 w-full">
            <CitationList citations={message.citations} />
          </div>
        )}

        {/* Footer: Time and Actions */}
        <div className={cn(
          'flex items-center gap-2 mt-2 px-1',
          isUser && 'flex-row-reverse'
        )}>
          <span className="text-[11px] text-muted-foreground">
            {formatTime(message.timestamp)}
          </span>

          {/* Copy button - only show for messages with content */}
          {message.content && !message.isStreaming && (
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleCopy}
                  className={cn(
                    'h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity',
                    copied && 'text-emerald-500'
                  )}
                >
                  {copied ? (
                    <Check className="h-3 w-3" />
                  ) : (
                    <Copy className="h-3 w-3" />
                  )}
                </Button>
              </TooltipTrigger>
              <TooltipContent side="top">
                <p>{copied ? 'Copied!' : 'Copy message'}</p>
              </TooltipContent>
            </Tooltip>
          )}
        </div>
      </div>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="flex flex-col gap-2 min-w-[200px]">
      <Skeleton className="h-3 w-[90%] bg-foreground/10" />
      <Skeleton className="h-3 w-[75%] bg-foreground/10" />
      <Skeleton className="h-3 w-[60%] bg-foreground/10" />
    </div>
  );
}

function formatTime(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);

  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;

  return date.toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
  });
}
