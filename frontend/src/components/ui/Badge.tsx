import React from 'react';

interface BadgeProps {
  value: number | null | undefined;
  suffix?: string;
  prefix?: string;
  showSign?: boolean;
}

export function Badge({ value, suffix = '%', prefix = '', showSign = true }: BadgeProps) {
  // Guard: valeur nulle → badge neutre
  if (value == null) {
    return (
      <span
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          padding: '0.25rem 0.5rem',
          borderRadius: '9999px',
          fontSize: '0.875rem',
          fontWeight: 600,
          backgroundColor: 'hsl(var(--bg-card-hover))',
          color: 'hsl(var(--text-muted))',
          border: '1px solid rgba(255,255,255,0.08)',
        }}
      >
        ---
      </span>
    );
  }

  const isPositive = value >= 0;
  const formattedValue = `${showSign && isPositive ? '+' : ''}${value.toFixed(2)}${suffix}`;

  const bgVar = isPositive ? '--success-faded' : '--danger-faded';
  const colorVar = isPositive ? '--success' : '--danger';
  const glowVar = isPositive ? 'rgba(33, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)';

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '0.25rem 0.5rem',
        borderRadius: '9999px',
        fontSize: '0.875rem',
        fontWeight: 600,
        backgroundColor: `hsl(var(${bgVar}))`,
        color: `hsl(var(${colorVar}))`,
        border: `1px solid hsl(var(${colorVar}) / 0.4)`,
        boxShadow: `0 0 10px ${glowVar}`
      }}
    >
      {prefix}{formattedValue}
    </span>
  );
}
