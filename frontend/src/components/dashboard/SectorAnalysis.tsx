'use client';

import React from 'react';
import { 
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend 
} from 'recharts';
import { Card } from '../ui/Card';

interface SectorData {
  secteur: string;
  volume_total: number;
  variation_moyenne: number;
  nb_actions: number;
}

interface SectorAnalysisProps {
  data: SectorData[];
}

const COLORS = [
  '#E69F00', // Orange vibrant
  '#56B4E9', // Bleu ciel clair
  '#009E73', // Vert d'eau (émeraude)
  '#F0E442', // Jaune éclatant
  '#0072B2', // Bleu sombre/marine
  '#D55E00', // Rouge vermillon / Brique
  '#CC79A7', // Rose / Fuchsia
  '#F5F5F5', // Blanc cassé / Gris très clair
  '#333333'  // Gris très sombre
];

export function SectorAnalysis({ data }: SectorAnalysisProps) {
  if (!data || data.length === 0) return null;

  // Trier par volume pour le PieChart
  const pieData = [...data].sort((a, b) => b.volume_total - a.volume_total);
  
  // Formateur pour le volume (K ou M)
  const formatVolume = (val: number) => {
    if (val >= 1000000) return `${(val / 1000000).toFixed(1)}M`;
    if (val >= 1000) return `${(val / 1000).toFixed(0)}K`;
    return val.toString();
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
      {/* Répartition du Volume */}
      <Card>
        <h3 style={{ fontSize: '1.1rem', marginBottom: '1.5rem', fontWeight: 600 }}>Répartition du Volume par Secteur</h3>
        <div style={{ height: '300px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="volume_total"
                nameKey="secteur"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(23, 23, 23, 0.9)', 
                  border: '1px solid hsl(var(--border-glass))',
                  borderRadius: '8px',
                  color: '#fff'
                }}
                formatter={(value: any) => [formatVolume(Number(value || 0)), 'Volume']}
              />
              <Legend verticalAlign="bottom" height={36}/>
            </PieChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Performance Moyenne */}
      <Card>
        <h3 style={{ fontSize: '1.1rem', marginBottom: '1.5rem', fontWeight: 600 }}>Performance Moyenne par Secteur</h3>
        <div style={{ height: '300px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" horizontal={false} />
              <XAxis 
                type="number" 
                domain={['dataMin - 0.5', 'dataMax + 0.5']} 
                tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }}
                tickFormatter={(val) => `${Number(val || 0).toFixed(2)}%`}
              />
              <YAxis 
                dataKey="secteur" 
                type="category" 
                tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 10 }} 
                width={100}
              />
              <Tooltip 
                cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                contentStyle={{ 
                  backgroundColor: 'rgba(23, 23, 23, 0.9)', 
                  border: '1px solid hsl(var(--border-glass))',
                  borderRadius: '8px',
                }}
                formatter={(value: any) => [`${Number(value || 0).toFixed(2)}%`, 'Variation Moy.']}
              />
              <Bar 
                dataKey="variation_moyenne" 
                radius={[0, 4, 4, 0]}
              >
                {data.map((entry, index) => (
                  <Cell 
                    key={`bar-${index}`} 
                    fill={entry.variation_moyenne >= 0 ? 'hsl(var(--success))' : 'hsl(var(--danger))'} 
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}
