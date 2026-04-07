import React from 'react';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

export interface IndexData {
  nom: string;
  valeur: number;
  variation: number;
}

interface MarketIndicesProps {
  indices: IndexData[];
  volume: number;
  dateMaj: string;
}

export function MarketIndices({ indices, volume, dateMaj }: MarketIndicesProps) {
  // Rendre le filtrage insensible a la casse
  const normalizedIndices = indices.map(i => ({ ...i, nom_lower: i.nom.toLowerCase().trim() }));
  
  // Noms normalises pour le filtrage
  const targetNames = ['brvm composite', 'brvm 30', 'brvm prestige'];
  
  // Filtrer et dedupliquer (au cas ou le scraper a insere deux fois avec une casse differente)
  const topIndices: IndexData[] = [];
  const seen = new Set();
  
  for (const name of targetNames) {
    const found = normalizedIndices.find(i => i.nom_lower === name);
    if (found && !seen.has(name)) {
      topIndices.push({
        nom: found.nom_lower === 'brvm composite' ? 'BRVM Composite' : 
             found.nom_lower === 'brvm 30' ? 'BRVM 30' : 'BRVM Prestige',
        valeur: found.valeur,
        variation: found.variation
      });
      seen.add(name);
    }
  }

  // Formatage de la date en francais
  const formattedDate = React.useMemo(() => {
    if (!dateMaj) return '';
    try {
      const d = new Date(dateMaj);
      return new Intl.DateTimeFormat('fr-FR', { 
        day: 'numeric', 
        month: 'long', 
        year: 'numeric' 
      }).format(d);
    } catch (e) {
      return dateMaj;
    }
  }, [dateMaj]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginBottom: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 800, marginBottom: '0.5rem', letterSpacing: '-0.02em', color: 'hsl(var(--text-bright))' }}>Vue d'Ensemble</h1>
          <p style={{ color: 'hsl(var(--text-muted))', fontSize: '1.1rem' }}>
            Marché BRVM — Séance du <span style={{ color: 'hsl(var(--accent-secondary))', fontWeight: 600 }}>{formattedDate}</span>
          </p>
        </div>
        <div style={{ textAlign: 'right' }}>
          <p style={{ color: 'hsl(var(--text-muted))', fontSize: '0.875rem' }}>Volume Quotidien</p>
          <p style={{ fontSize: '1.25rem', fontWeight: 600, color: 'hsl(var(--accent-primary))' }}>
            {new Intl.NumberFormat('fr-FR').format(volume)} Titres
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
        {topIndices.map((idx) => (
          <Card key={idx.nom} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ color: 'hsl(var(--text-muted))', fontSize: '0.875rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                {idx.nom}
              </h3>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', marginTop: '0.25rem', fontFamily: 'var(--font-outfit)' }}>
                {idx.valeur != null ? idx.valeur.toFixed(2) : '---'}
              </div>
            </div>
            <Badge value={idx.variation} />
          </Card>
        ))}
      </div>
    </div>
  );
}
