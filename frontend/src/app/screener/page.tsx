import { brvmAPI } from '@/lib/api';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import Link from 'next/link';

export default async function ScreenerPage() {
  let screenerData;
  try {
    screenerData = await brvmAPI.getScreener();
  } catch (error) {
    return (
      <div className="animate-fade-in">
        <h1 style={{ fontSize: '2rem', marginBottom: '1rem', color: 'hsl(var(--danger))' }}>Erreur</h1>
        <p>Impossible de se charger les données du Screener.</p>
      </div>
    );
  }

  // Trier par defaut par Ticker
  const sortedData = [...screenerData].sort((a, b) => a.ticker.localeCompare(b.ticker));

  return (
    <div className="animate-fade-in" style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Screener Actions</h1>
        <p style={{ color: 'hsl(var(--text-muted))' }}>Analysez toutes les actions listées à la BRVM</p>
      </div>

      <Card noPadding style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid hsl(var(--border-glass))', backgroundColor: 'hsl(var(--bg-glass))' }}>
              <th style={{ padding: '1rem 1.5rem', color: 'hsl(var(--text-muted))', fontWeight: 600, fontSize: '0.875rem' }}>Ticker</th>
              <th style={{ padding: '1rem 1.5rem', color: 'hsl(var(--text-muted))', fontWeight: 600, fontSize: '0.875rem' }}>Nom / Entreprise</th>
              <th style={{ padding: '1rem 1.5rem', color: 'hsl(var(--text-muted))', fontWeight: 600, fontSize: '0.875rem' }}>Secteur</th>
              <th style={{ padding: '1rem 1.5rem', color: 'hsl(var(--text-muted))', fontWeight: 600, fontSize: '0.875rem', textAlign: 'right' }}>Prix (FCFA)</th>
              <th style={{ padding: '1rem 1.5rem', color: 'hsl(var(--text-muted))', fontWeight: 600, fontSize: '0.875rem', textAlign: 'right' }}>Variation</th>
              <th style={{ padding: '1rem 1.5rem', color: 'hsl(var(--text-muted))', fontWeight: 600, fontSize: '0.875rem', textAlign: 'right' }}>Volume</th>
            </tr>
          </thead>
          <tbody>
            {sortedData.map((item, idx) => (
              <tr 
                key={item.ticker} 
                style={{ 
                  borderBottom: idx === sortedData.length - 1 ? 'none' : '1px solid hsl(var(--border-glass))',
                  transition: 'background-color 0.2s',
                  cursor: 'pointer'
                }}
                className="hover-nav"
              >
                <td style={{ padding: '1rem 1.5rem', fontWeight: 600, color: 'hsl(var(--accent-primary))' }}>
                  <Link href={`/actions/${item.ticker}`}>{item.ticker}</Link>
                </td>
                <td style={{ padding: '1rem 1.5rem' }}>{item.nom}</td>
                <td style={{ padding: '1rem 1.5rem', color: 'hsl(var(--text-muted))', fontSize: '0.875rem' }}>
                  {item.secteur || '-'}
                </td>
                <td style={{ padding: '1rem 1.5rem', textAlign: 'right', fontFamily: 'var(--font-outfit)', fontSize: '1.125rem' }}>
                  {new Intl.NumberFormat('fr-FR').format(item.prix)}
                </td>
                <td style={{ padding: '1rem 1.5rem', textAlign: 'right' }}>
                  <Badge value={item.variation} />
                </td>
                <td style={{ padding: '1rem 1.5rem', textAlign: 'right', color: 'hsl(var(--text-muted))' }}>
                  {new Intl.NumberFormat('fr-FR').format(item.volume)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
