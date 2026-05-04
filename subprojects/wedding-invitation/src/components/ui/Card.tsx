import { cn } from '@/lib/utils';
import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
}

export function Card({ children, className }: CardProps) {
  return (
    <div
      className={cn(
        'bg-gradient-to-b from-[rgba(255,251,245,0.9)] to-[rgba(255,247,238,0.82)] border border-[rgba(120,86,55,0.14)] shadow-soft backdrop-blur-md rounded-panel p-8',
        className
      )}
    >
      {children}
    </div>
  );
}
