import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { TokenBudget } from './TokenBudget';

describe('TokenBudget', () => {
  it('renders token count with formatted numbers', () => {
    render(<TokenBudget used={1500} max={4096} />);

    expect(screen.getByText('Token Budget')).toBeInTheDocument();
    // Use regex to find the formatted numbers in the combined text
    expect(screen.getByText(/1,500/)).toBeInTheDocument();
    expect(screen.getByText(/4,096/)).toBeInTheDocument();
  });

  it('calculates correct percentage width', () => {
    render(<TokenBudget used={2048} max={4096} />);

    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveStyle({ width: '50%' });
  });

  it('applies warning color when usage > 70%', () => {
    render(<TokenBudget used={3000} max={4096} />);

    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveClass('bg-amber-500');
    expect(progressBar).not.toHaveClass('bg-destructive');
  });

  it('applies critical color when usage > 90%', () => {
    render(<TokenBudget used={3800} max={4096} />);

    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveClass('bg-destructive');
  });

  it('applies primary color when usage is low', () => {
    render(<TokenBudget used={1000} max={4096} />);

    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveClass('bg-primary');
    expect(progressBar).not.toHaveClass('bg-amber-500');
    expect(progressBar).not.toHaveClass('bg-destructive');
  });

  it('caps percentage at 100% even if used exceeds max', () => {
    render(<TokenBudget used={5000} max={4096} />);

    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveStyle({ width: '100%' });
  });

  it('has correct aria attributes', () => {
    render(<TokenBudget used={1500} max={4096} />);

    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveAttribute('aria-valuenow', '1500');
    expect(progressBar).toHaveAttribute('aria-valuemin', '0');
    expect(progressBar).toHaveAttribute('aria-valuemax', '4096');
    expect(progressBar).toHaveAttribute('aria-label', 'Token usage: 1500 of 4096');
  });
});
