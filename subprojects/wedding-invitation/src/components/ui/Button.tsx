import { cn } from '@/lib/utils';
import type { ReactNode } from 'react';

interface ButtonProps {
  children: ReactNode;
  variant?: 'primary' | 'secondary';
  className?: string;
  onClick?: () => void;
  type?: 'button' | 'submit';
  disabled?: boolean;
  href?: string;
  /** Opens in a new tab (maps, WhatsApp web, etc.) */
  external?: boolean;
}

export function Button({
  children,
  variant = 'primary',
  className,
  onClick,
  type = 'button',
  disabled,
  href,
  external,
}: ButtonProps) {
  const classes = cn(
    'inline-flex items-center justify-center min-h-[48px] px-6 rounded-pill font-medium text-[0.95rem] transition-all duration-180 cursor-pointer border-none',
    variant === 'primary' &&
      'text-[#fffaf4] bg-gradient-to-br from-bronze-500 to-[#bd8760] shadow-accent hover:-translate-y-0.5 hover:shadow-[0_20px_40px_rgba(139,94,60,0.3)] active:translate-y-0',
    variant === 'secondary' &&
      'text-green-800 bg-[rgba(255,252,248,0.76)] border border-[rgba(120,86,55,0.16)] hover:-translate-y-0.5 hover:bg-[rgba(255,252,248,0.9)] active:translate-y-0',
    disabled && 'opacity-50 cursor-not-allowed hover:translate-y-0',
    className
  );

  if (href) {
    return (
      <a
        href={href}
        className={classes}
        {...(external ? { target: '_blank', rel: 'noopener noreferrer' } : {})}
      >
        {children}
      </a>
    );
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={classes}
    >
      {children}
    </button>
  );
}
