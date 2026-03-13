/**
 * Citation component with expandable snippet
 */

import { useState } from 'react';
import type { Citation as CitationType } from '../types';

interface CitationProps {
  citation: CitationType;
}

export function Citation({ citation }: CitationProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const fileName = citation.file_path.split('/').pop() || citation.file_path;
  const scorePercent = Math.round(citation.score * 100);

  return (
    <div className="ask-docs-citation">
      <button
        className="ask-docs-citation-header"
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
      >
        <span className="ask-docs-citation-badge">[{citation.id}]</span>
        <span className="ask-docs-citation-file">{fileName}</span>
        <span className="ask-docs-citation-score">{scorePercent}%</span>
        <span className={`ask-docs-citation-arrow ${isExpanded ? 'expanded' : ''}`}>
          ▼
        </span>
      </button>

      {isExpanded && (
        <div className="ask-docs-citation-content">
          <p className="ask-docs-citation-snippet">{citation.snippet}</p>
          <div className="ask-docs-citation-meta">
            <span>Source: {citation.file_path}</span>
            <span>Chunk: {citation.chunk_id}</span>
          </div>
        </div>
      )}
    </div>
  );
}

interface CitationListProps {
  citations: CitationType[];
}

export function CitationList({ citations }: CitationListProps) {
  if (!citations.length) return null;

  return (
    <div className="ask-docs-citations">
      <h4 className="ask-docs-citations-title">Sources</h4>
      {citations.map((citation) => (
        <Citation key={`${citation.doc_id}-${citation.chunk_id}`} citation={citation} />
      ))}
    </div>
  );
}
