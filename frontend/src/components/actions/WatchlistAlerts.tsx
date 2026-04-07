'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '../ui/Card';
import Link from 'next/link';

interface Alert {
  ticker: string;
  targetPrice: number;
  condition: 'above' | 'below';
}

interface WatchlistAlertsProps {
  currentPrices: Record<string, number>; // ticker -> price
}

export function WatchlistAlerts({ currentPrices }: WatchlistAlertsProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [newTicker, setNewTicker] = useState('');
  const [newPrice, setNewPrice] = useState('');
  const [newCondition, setNewCondition] = useState<'above' | 'below'>('above');

  // Charger les alertes au démarrage
  useEffect(() => {
    const saved = localStorage.getItem('brvm_alerts');
    if (saved) {
      try {
        setAlerts(JSON.parse(saved));
      } catch (e) {
        console.error("Failed to parse alerts", e);
      }
    }
  }, []);

  // Sauvegarder les alertes
  const saveAlerts = (updatedAlerts: Alert[]) => {
    setAlerts(updatedAlerts);
    localStorage.setItem('brvm_alerts', JSON.stringify(updatedAlerts));
  };

  const addAlert = () => {
    if (!newTicker || !newPrice) return;
    const ticker = newTicker.toUpperCase().trim();
    const price = parseFloat(newPrice);
    if (isNaN(price)) return;

    const newAlert: Alert = { ticker, targetPrice: price, condition: newCondition };
    saveAlerts([...alerts, newAlert]);
    setNewTicker('');
    setNewPrice('');
  };

  const removeAlert = (index: number) => {
    const updated = alerts.filter((_, i) => i !== index);
    saveAlerts(updated);
  };

  // Vérifier les déclenchements
  const checkTrigger = (alert: Alert) => {
    const current = currentPrices[alert.ticker];
    if (current === undefined) return false;
    if (alert.condition === 'above') return current >= alert.targetPrice;
    if (alert.condition === 'below') return current <= alert.targetPrice;
    return false;
  };

  return (
    <Card style={{ marginBottom: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontSize: '1.5rem' }}>🔔</span> Mes Alertes de Prix
        </h3>
        <span style={{ fontSize: '0.8rem', color: 'hsl(var(--text-muted))' }}>
          {alerts.length} alerte(s) active(s)
        </span>
      </div>

      {/* Formulaire d'ajout */}
      <div style={{ 
        display: 'flex', 
        gap: '0.75rem', 
        marginBottom: '2rem', 
        padding: '1rem', 
        background: 'rgba(255,255,255,0.03)', 
        borderRadius: '12px',
        flexWrap: 'wrap'
      }}>
        <input 
          type="text" 
          placeholder="Ticker (ex: SGBC)" 
          value={newTicker}
          onChange={(e) => setNewTicker(e.target.value)}
          style={{ 
            background: 'hsl(var(--bg-card))', 
            border: '1px solid hsl(var(--border-glass))', 
            padding: '0.5rem 1rem', 
            borderRadius: '8px',
            color: '#fff',
            flex: 1,
            minWidth: '120px'
          }}
        />
        <select 
          value={newCondition}
          onChange={(e) => setNewCondition(e.target.value as 'above' | 'below')}
          style={{ 
            background: 'hsl(var(--bg-card))', 
            border: '1px solid hsl(var(--border-glass))', 
            padding: '0.5rem 1rem', 
            borderRadius: '8px',
            color: '#fff'
          }}
        >
          <option value="above">Prix ≥</option>
          <option value="below">Prix ≤</option>
        </select>
        <input 
          type="number" 
          placeholder="Prix Cible" 
          value={newPrice}
          onChange={(e) => setNewPrice(e.target.value)}
          style={{ 
            background: 'hsl(var(--bg-card))', 
            border: '1px solid hsl(var(--border-glass))', 
            padding: '0.5rem 1rem', 
            borderRadius: '8px',
            color: '#fff',
            width: '120px'
          }}
        />
        <button 
          onClick={addAlert}
          style={{ 
            background: 'hsl(var(--accent-primary))', 
            color: '#000', 
            border: 'none', 
            padding: '0.5rem 1.5rem', 
            borderRadius: '8px',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          Ajouter
        </button>
      </div>

      {/* Liste des alertes */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
        {alerts.length === 0 ? (
          <p style={{ gridColumn: '1/-1', textAlign: 'center', color: 'hsl(var(--text-muted))', padding: '2rem' }}>
            Aucune alerte configurée. Surveillez vos actions favorites !
          </p>
        ) : (
          alerts.map((alert, idx) => {
            const isTriggered = checkTrigger(alert);
            const current = currentPrices[alert.ticker];
            
            return (
              <div key={idx} style={{ 
                padding: '1rem', 
                borderRadius: '12px', 
                border: `1px solid ${isTriggered ? 'hsl(var(--success))' : 'hsl(var(--border-glass))'}`,
                background: isTriggered ? 'hsla(var(--success-h), var(--success-s), var(--success-l), 0.05)' : 'rgba(255,255,255,0.02)',
                position: 'relative',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Link href={`/actions/${alert.ticker}`} style={{ fontWeight: 700, fontSize: '1.1rem', color: 'hsl(var(--text-bright))', textDecoration: 'none' }}>
                      {alert.ticker}
                    </Link>
                    {isTriggered && <span style={{ fontSize: '0.7rem', background: 'hsl(var(--success))', color: '#000', padding: '0.1rem 0.4rem', borderRadius: '4px', fontWeight: 700 }}>HIT!</span>}
                  </div>
                  <p style={{ fontSize: '0.8rem', color: 'hsl(var(--text-muted))', marginTop: '0.2rem' }}>
                    Cible : {alert.condition === 'above' ? '≥' : '≤'} {alert.targetPrice} FCFA
                  </p>
                  {current !== undefined && (
                    <p style={{ fontSize: '0.85rem', fontWeight: 500, marginTop: '0.5rem', color: isTriggered ? 'hsl(var(--success))' : 'inherit' }}>
                      Cours : {current} FCFA
                    </p>
                  )}
                </div>
                <button 
                  onClick={() => removeAlert(idx)}
                  style={{ 
                    background: 'transparent', 
                    border: 'none', 
                    color: 'hsl(var(--danger))', 
                    cursor: 'pointer',
                    fontSize: '1.2rem',
                    padding: '0.5rem'
                  }}
                  title="Supprimer l'alerte"
                >
                  ×
                </button>
              </div>
            );
          })
        )}
      </div>
    </Card>
  );
}
