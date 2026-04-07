import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  noPadding?: boolean;
}

export function Card({ children, className = '', style, noPadding = false }: CardProps) {
  return (
    <div
      className={`glass-panel card-hover ${className}`}
      style={{
        padding: noPadding ? '0' : '1.5rem',
        ...style
      }}
    >
      {children}
    </div>
  );
}
