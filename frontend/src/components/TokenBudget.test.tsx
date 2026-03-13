import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { TokenBudget } from './TokenBudget';

describe('TokenBudget', () => {
  it('renders token count with formatted numbers', () => {
    render(<TokenBudget used={1500} max={4096} />);

    expect(screen.getByText('Token Budget')).toBeInTheDocument();
    expect(screen.getByText('~1,500 / 4,096')).toBeInTheDocument();
  });

  it('calculates correct percentage width', () => {
    const { container } = render(<TokenBudget used={2048} max={4096} />);

    const fill = container.querySelector('.ask-docs-token-fill');
    expect(fill).toHaveStyle({ width: '50%' });
  });

  it('applies warning class when usage > 70%', () => {
    const { container } = render(<TokenBudget used={3000} max={4096} />);

    const fill = container.querySelector('.ask-docs-token-fill');
    expect(fill).toHaveClass('warning');
    expect(fill).not.toHaveClass('critical');
  });

  it('applies critical class when usage > 90%', () => {
    const { container } = render(<TokenBudget used={3800} max={4096} />);

    const fill = container.querySelector('.ask-docs-token-fill');
    expect(fill).toHaveClass('critical');
  });

  it('does not apply warning/critical class when usage is low', () => {
    const { container } = render(<TokenBudget used={1000} max={4096} />);

    const fill = container.querySelector('.ask-docs-token-fill');
    expect(fill).not.toHaveClass('warning');
    expect(fill).not.toHaveClass('critical');
  });

  it('caps percentage at 100% even if used exceeds max', () => {
    const { container } = render(<TokenBudget used={5000} max={4096} />);

    const fill = container.querySelector('.ask-docs-token-fill');
    expect(fill).toHaveStyle({ width: '100%' });
  });

  it('handles zero max gracefully', () => {
    render(<TokenBudget used={0} max={0} />);
    expect(screen.getByText('~0 / 0')).toBeInTheDocument();
  });
});
