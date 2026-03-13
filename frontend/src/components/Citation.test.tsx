import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Citation, CitationList } from './Citation';
import type { Citation as CitationType } from '../types';

const mockCitation: CitationType = {
  id: 1,
  doc_id: 'doc-123',
  chunk_id: 0,
  file_path: 'docs/getting-started.md',
  snippet: 'This is a sample snippet from the documentation that explains the feature.',
  score: 0.87,
};

describe('Citation', () => {
  it('renders citation with file name and score', () => {
    render(<Citation citation={mockCitation} index={0} />);

    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('getting-started.md')).toBeInTheDocument();
    expect(screen.getByText('87')).toBeInTheDocument();
  });

  it('is collapsed by default', () => {
    render(<Citation citation={mockCitation} index={0} />);

    expect(screen.queryByText(mockCitation.snippet)).not.toBeInTheDocument();
  });

  it('expands when clicked to show snippet', () => {
    render(<Citation citation={mockCitation} index={0} />);

    const button = screen.getByRole('button');
    fireEvent.click(button);

    expect(screen.getByText(mockCitation.snippet)).toBeInTheDocument();
  });

  it('collapses when clicked again', () => {
    render(<Citation citation={mockCitation} index={0} />);

    const button = screen.getByRole('button');
    fireEvent.click(button); // Expand
    expect(screen.getByText(mockCitation.snippet)).toBeInTheDocument();

    fireEvent.click(button); // Collapse
    expect(screen.queryByText(mockCitation.snippet)).not.toBeInTheDocument();
  });

  it('has correct aria-expanded attribute', () => {
    render(<Citation citation={mockCitation} index={0} />);

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-expanded', 'false');

    fireEvent.click(button);
    expect(button).toHaveAttribute('aria-expanded', 'true');
  });
});

describe('CitationList', () => {
  const mockCitations: CitationType[] = [
    mockCitation,
    {
      id: 2,
      doc_id: 'doc-456',
      chunk_id: 1,
      file_path: 'docs/api-reference.md',
      snippet: 'API documentation content',
      score: 0.75,
    },
  ];

  it('renders nothing when citations array is empty', () => {
    const { container } = render(<CitationList citations={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders title and all citations', () => {
    render(<CitationList citations={mockCitations} />);

    expect(screen.getByText(/Sources/)).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('getting-started.md')).toBeInTheDocument();
    expect(screen.getByText('api-reference.md')).toBeInTheDocument();
  });
});
