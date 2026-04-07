'use client';

import React, { useEffect, useState } from 'react';
import { Card } from '../ui/Card';
import { brvmAPI } from '@/lib/api';

export function MacroPanel() {
  const [commodities, setCommodities] = useState<any[]>([]);
  const [indicators, setIndicators] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMacroData = async () => {
      try {
        const [commData, indData] = await Promise.all([
          brvmAPI.getMacroCommodities(),
          brvmAPI.getMacroIndicators()
        ]);
        setCommodities(commData.value || []);
        
        // On prend les indicateurs majeurs, on groupe par pays
        // On affiche idéalement l'UEMOA en premier si possible ou juste la liste globale
        setIndicators(indData.value || []);
      } catch (error) {
        console.error("Erreur chargement macro:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchMacroData();
  }, []);

  if (loading) {
    return (
      <Card>
        <div style={{ height: '150px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <span style={{ color: 'var(--text-muted)' }}>Chargement Macro (En Direct)...</span>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <h2 style={{ 
        fontSize: '1rem', 
        fontWeight: 700, 
        color: 'var(--gold)', 
        textTransform: 'uppercase', 
        letterSpacing: '0.08em', 
        marginBottom: '1.5rem',
        borderBottom: '1px solid var(--border)',
        paddingBottom: '0.75rem'
      }}>
        Macro-Économie & Matières Premières
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '3rem' }}>
        
        {/* Colonne 1: Matières premières */}
        <div>
          <h3 style={{ 
            fontSize: '0.85rem', 
            marginBottom: '1rem', 
            fontWeight: 600, 
            color: 'var(--text-muted)', 
            textTransform: 'uppercase', 
            letterSpacing: '0.06em' 
          }}>
            Matières premières (Temps Réel)
          </h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {commodities.map((comm) => {
              const isUp = comm.variation_jour && comm.variation_jour >= 0;
              return (
                <div key={comm.symbole + comm.nom} style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  alignItems: 'center', 
                  padding: '0.6rem 0',
                  borderBottom: '1px solid var(--border-glass)' 
                }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{comm.nom}</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                      {comm.symbole}/{comm.unite}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: 700, fontSize: '1.05rem', fontFamily: 'var(--font-mono, monospace)' }}>
                      {comm.prix?.toLocaleString('fr-FR', { minimumFractionDigits: 2 }) || 'N/A'}
                    </div>
                    <div style={{ 
                      fontSize: '0.8rem', 
                      color: isUp ? 'var(--success)' : 'var(--danger)',
                      backgroundColor: isUp ? 'rgba(34, 197, 94, 0.12)' : 'rgba(239, 68, 68, 0.12)',
                      padding: '1px 7px',
                      borderRadius: '4px',
                      marginTop: '3px',
                      display: 'inline-block',
                      fontWeight: 600
                    }}>
                      {isUp ? '+' : ''}{comm.variation_jour}%
                    </div>
                  </div>
                </div>
              );
            })}
            {commodities.length === 0 && (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', padding: '1rem 0' }}>
                Yahoo Finance API temporairement indisponible.
              </div>
            )}
          </div>
        </div>

        {/* Colonne 2: Indicateurs Macro BCEAO / FMI */}
        <div>
          <h3 style={{ 
            fontSize: '0.85rem', 
            marginBottom: '1rem', 
            fontWeight: 600, 
            color: 'var(--text-muted)', 
            textTransform: 'uppercase', 
            letterSpacing: '0.06em' 
          }}>
            Indicateurs Macro (FMI / BCEAO)
          </h3>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)' }}>
                <th style={{ textAlign: 'left', padding: '0.4rem 0.5rem', fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 500 }}>Zone / Pays</th>
                <th style={{ textAlign: 'center', padding: '0.4rem 0.5rem', fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 500 }}>Année</th>
                <th style={{ textAlign: 'right', padding: '0.4rem 0.5rem', fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 500 }}>Croiss. PIB</th>
                <th style={{ textAlign: 'right', padding: '0.4rem 0.5rem', fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 500 }}>Inflation</th>
                <th style={{ textAlign: 'right', padding: '0.4rem 0.5rem', fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 500 }}>Bancarisation</th>
              </tr>
            </thead>
            <tbody>
              {indicators.slice(0, 10).map((ind, i) => (
                <tr key={i} style={{ borderBottom: '1px solid var(--border-glass)' }}>
                  <td style={{ padding: '0.7rem 0.5rem', fontWeight: 600, fontSize: '0.92rem' }}>{ind.pays}</td>
                  <td style={{ padding: '0.7rem 0.5rem', color: 'var(--text-muted)', textAlign: 'center', fontSize: '0.85rem' }}>{ind.annee}</td>
                  <td style={{ 
                    padding: '0.7rem 0.5rem', 
                    textAlign: 'right', 
                    fontWeight: 700, 
                    fontSize: '0.92rem',
                    fontFamily: 'var(--font-mono, monospace)',
                    color: ind.croissance_pib > 0 ? 'var(--success)' : 'var(--danger)' 
                  }}>
                    {ind.croissance_pib != null ? `${ind.croissance_pib > 0 ? '+' : ''}${Number(ind.croissance_pib).toFixed(1)}%` : '--'}
                  </td>
                  <td style={{ 
                    padding: '0.7rem 0.5rem', 
                    textAlign: 'right', 
                    fontWeight: 700,
                    fontSize: '0.92rem',
                    fontFamily: 'var(--font-mono, monospace)',
                    color: ind.inflation > 3.0 ? 'var(--danger)' : 'var(--success)' 
                  }}>
                    {ind.inflation != null ? `${Number(ind.inflation).toFixed(1)}%` : '--'}
                  </td>
                  <td style={{ 
                    padding: '0.7rem 0.5rem', 
                    textAlign: 'right',
                    fontSize: '0.88rem',
                    color: 'var(--text-secondary)' 
                  }}>
                    {ind.taux_bancarisation != null ? `${Number(ind.taux_bancarisation).toFixed(0)}%` : '--'}
                  </td>
                </tr>
              ))}
              {indicators.length === 0 && (
                <tr>
                  <td colSpan={5} style={{ padding: '1.5rem 0.5rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    Aucun indicateur macro disponible en base.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

      </div>
    </Card>
  );
}
