/**
 * Citation component with expandable snippet and modern design
 */

import { useState } from 'react';
import { ChevronDown, FileText, Hash, Percent } from 'lucide-react';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';
import { Badge } from './ui/badge';
import { cn } from '../lib/utils';
import type { Citation as CitationType } from '../types';

interface CitationProps {
  citation: CitationType;
  index: number;
}

export function Citation({ citation, index }: CitationProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const fileName = citation.file_path.split('/').pop() || citation.file_path;
  const scorePercent = Math.round(citation.score * 100);

  // Determine score color
  const scoreColor = scorePercent >= 80 ? 'success' : scorePercent >= 60 ? 'warning' : 'secondary';

  return (
    <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
      <div className={cn(
        'rounded-lg border border-border bg-card overflow-hidden transition-all duration-200',
        'hover:border-border/80 hover:shadow-sm',
        isExpanded && 'ring-1 ring-primary/20'
      )}>
        <CollapsibleTrigger asChild>
          <button
            className="w-full flex items-center gap-3 px-3 py-2.5 text-left hover:bg-accent/50 transition-colors"
            aria-expanded={isExpanded}
          >
            {/* Citation Number Badge */}
            <Badge variant="default" className="h-5 min-w-[24px] px-1.5 text-[10px]">
              {index + 1}
            </Badge>

            {/* File Icon */}
            <div className="flex items-center justify-center w-7 h-7 rounded-md bg-muted">
              <FileText className="w-3.5 h-3.5 text-muted-foreground" />
            </div>

            {/* File Name */}
            <span className="flex-1 text-sm font-medium text-foreground truncate">
              {fileName}
            </span>

            {/* Score */}
            <Badge variant={scoreColor} className="gap-1 h-5 text-[10px]">
              <Percent className="w-2.5 h-2.5" />
              {scorePercent}
            </Badge>

            {/* Expand Icon */}
            <ChevronDown
              className={cn(
                'w-4 h-4 text-muted-foreground transition-transform duration-200',
                isExpanded && 'rotate-180'
              )}
            />
          </button>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <div className="px-3 pb-3 pt-1 space-y-3 animate-fade-in">
            {/* Snippet */}
            <div className="relative">
              <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-primary rounded-full" />
              <p className="pl-3 text-sm text-foreground/90 leading-relaxed">
                {citation.snippet}
              </p>
            </div>

            {/* Metadata */}
            <div className="flex flex-wrap items-center gap-3 pt-1">
              <MetaItem icon={FileText} label="Source" value={citation.file_path} />
              <MetaItem icon={Hash} label="Chunk" value={String(citation.chunk_id)} />
            </div>
          </div>
        </CollapsibleContent>
      </div>
    </Collapsible>
  );
}

interface MetaItemProps {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  value: string;
}

function MetaItem({ icon: Icon, label, value }: MetaItemProps) {
  return (
    <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
      <Icon className="w-3 h-3" />
      <span className="font-medium">{label}:</span>
      <span className="truncate max-w-[150px]" title={value}>
        {value}
      </span>
    </div>
  );
}

interface CitationListProps {
  citations: CitationType[];
}

export function CitationList({ citations }: CitationListProps) {
  if (!citations.length) return null;

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <div className="h-px flex-1 bg-border" />
        <span className="text-[10px] font-semibold text-muted-foreground uppercase tracking-wider">
          Sources ({citations.length})
        </span>
        <div className="h-px flex-1 bg-border" />
      </div>

      <div className="space-y-2">
        {citations.map((citation, index) => (
          <Citation
            key={`${citation.doc_id}-${citation.chunk_id}`}
            citation={citation}
            index={index}
          />
        ))}
      </div>
    </div>
  );
}
