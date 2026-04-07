import React from 'react';
import { Badge } from '../ui/Badge';
import { Card } from '../ui/Card';

interface ActionHeaderProps {
  ticker: string;
  nom: string;
  secteur: string | null;
  prix?: number;
  variation?: number;
}

export function ActionHeader({ ticker, nom, secteur, prix, variation }: ActionHeaderProps) {
  return (
    <Card style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.25rem' }}>
          <h1 style={{ fontSize: '2.5rem', color: 'hsl(var(--text-main))', lineHeight: 1 }}>{ticker}</h1>
          <span style={{ backgroundColor: 'hsl(var(--bg-card-hover))', padding: '0.25rem 0.75rem', borderRadius: '4px', fontSize: '0.875rem', color: 'hsl(var(--text-muted))' }}>
            {secteur || 'Secteur Non Défini'}
          </span>
        </div>
        <h2 style={{ fontSize: '1.25rem', color: 'hsl(var(--text-muted))', fontWeight: 400 }}>{nom}</h2>
      </div>

      {prix != null && (
        <div style={{ textAlign: 'right' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', justifyContent: 'flex-end' }}>
             <span style={{ fontSize: '2.5rem', fontWeight: 700, fontFamily: 'var(--font-outfit)' }}>
              {new Intl.NumberFormat('fr-FR').format(prix)} <span style={{ fontSize: '1rem', color: 'hsl(var(--text-muted))', fontWeight: 400 }}>FCFA</span>
            </span>
          </div>
          <div style={{ marginTop: '0.5rem' }}>
            <Badge value={variation} />
          </div>
        </div>
      )}
    </Card>
  );
}
