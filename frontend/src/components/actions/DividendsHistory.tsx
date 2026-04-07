'use client';

import React from 'react';
import { Card } from '../ui/Card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface Dividende {
  annee_exercice: number;
  date_ex_dividende: string;
  date_paiement: string;
  montant_net: number;
  rendement_calcul: number;
  payout_ratio: number;
}

interface DividendsHistoryProps {
  dividends: Dividende[];
}

export function DividendsHistory({ dividends }: DividendsHistoryProps) {
  if (!dividends || dividends.length === 0) {
    return (
      <Card style={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p style={{ color: 'hsl(var(--text-muted))' }}>Aucun historique de dividendes disponible.</p>
      </Card>
    );
  }

  // Trier par année croissante pour le graphique
  const sortedDividends = [...dividends].sort((a, b) => a.annee_exercice - b.annee_exercice);

  return (
    <Card style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: 600, margin: 0 }}>
          Historique des Dividendes
        </h3>
      </div>
      
      <div style={{ height: '300px', width: '100%', marginTop: '1rem' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={sortedDividends} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
            <XAxis 
              dataKey="annee_exercice" 
              tick={{ fill: 'hsl(var(--text-muted))', fontSize: 12 }} 
              axisLine={{ stroke: 'rgba(255,255,255,0.1)' }}
            />
            <YAxis 
              tick={{ fill: 'hsl(var(--text-muted))', fontSize: 12 }} 
              axisLine={false}
              tickLine={false}
              tickFormatter={(val) => `${val} F`}
            />
            <Tooltip 
               contentStyle={{ 
                 backgroundColor: 'rgba(13, 20, 32, 0.95)', 
                 border: '1px solid hsl(var(--border-glass))',
                 borderRadius: '8px',
                 color: '#fff',
                 fontFamily: 'var(--font-ui)'
               }}
               formatter={(value: any, name: any) => {
                 if (name === "montant_net") return [`${value} FCFA`, "Dividende Net"];
                 if (name === "payout_ratio") return [`${value}%`, "Payout Ratio"];
                 return [value, name];
               }}
               labelStyle={{ color: 'hsl(var(--gold))', fontWeight: 'bold' }}
            />
            <Bar 
              dataKey="montant_net" 
              radius={[4, 4, 0, 0]}
              maxBarSize={50}
            >
              {sortedDividends.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={entry.payout_ratio && entry.payout_ratio > 80 ? 'hsl(var(--danger))' : 'hsl(var(--gold))'} 
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', marginTop: '0.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: 'hsl(var(--text-muted))' }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: 'hsl(var(--gold))', borderRadius: '2px' }}></div>
          <span>Dividende Soutenable (Payout ≤ 80%)</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: 'hsl(var(--text-muted))' }}>
          <div style={{ width: '12px', height: '12px', backgroundColor: 'hsl(var(--danger))', borderRadius: '2px' }}></div>
          <span>Risque coupure (Payout &gt; 80%)</span>
        </div>
      </div>
    </Card>
  );
}
