import React from 'react';
import { Card } from '../ui/Card';

interface Dividende {
  date_ex_dividende?: string;
  date_paiement?: string;
  montant_net: number;
  rendement_calcul?: number;
}

interface DividendsListProps {
  dividendes: Dividende[];
}

export function DividendsList({ dividendes }: DividendsListProps) {
  if (!dividendes || dividendes.length === 0) {
    return (
      <Card style={{ height: '100%' }}>
        <h3 style={{ marginBottom: '1rem', fontSize: '1.125rem' }}>Dividendes</h3>
        <p style={{ color: 'hsl(var(--text-muted))' }}>Aucun dividende récent listé pour cette action.</p>
      </Card>
    );
  }

  return (
    <Card style={{ height: '100%', overflowY: 'auto' }}>
      <h3 style={{ marginBottom: '1.5rem', fontSize: '1.125rem' }}>Historique des Dividendes</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {dividendes.map((div, idx) => (
          <div key={idx} style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            paddingBottom: '1rem',
            borderBottom: idx === dividendes.length - 1 ? 'none' : '1px solid hsl(var(--border-glass))'
          }}>
            <div>
               <p style={{ fontWeight: 600, color: 'hsl(var(--success))', fontSize: '1.125rem' }}>
                 {new Intl.NumberFormat('fr-FR').format(div.montant_net)} FCFA
               </p>
               <p style={{ color: 'hsl(var(--text-muted))', fontSize: '0.875rem' }}>
                Paiement : {div.date_paiement ? new Date(div.date_paiement).toLocaleDateString('fr-FR') : 'Non défini'}
               </p>
            </div>
            {div.rendement_calcul ? (
              <div style={{ textAlign: 'right', backgroundColor: 'hsl(var(--bg-glass))', padding: '0.5rem', borderRadius: '8px' }}>
                <span style={{ display: 'block', fontSize: '0.75rem', color: 'hsl(var(--text-muted))' }}>Rendement</span>
                <span style={{ fontWeight: 600, color: 'hsl(var(--accent-primary))' }}>{div.rendement_calcul}%</span>
              </div>
            ) : null}
          </div>
        ))}
      </div>
    </Card>
  );
}
