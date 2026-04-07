import { brvmAPI } from '@/lib/api';
import { MarketIndices } from '@/components/dashboard/MarketIndices';
import { SectorAnalysis } from '@/components/dashboard/SectorAnalysis';
import { WatchlistAlerts } from '@/components/actions/WatchlistAlerts';
import { MacroPanel } from '@/components/dashboard/MacroPanel';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import Link from 'next/link';

export default async function DashboardPage() {
  let summary;
  let sectorData = [];
  let screener = [];
  try {
    const [summaryRes, sectorRes, screenerRes] = await Promise.all([
      brvmAPI.getMarketSummary(),
      brvmAPI.getSectorPerformance(),
      brvmAPI.getScreener()
    ]);
    summary = summaryRes;
    sectorData = sectorRes;
    screener = screenerRes;
  } catch (error) {
    return (
      <div className="animate-fade-in">
        <h1 style={{ fontSize: '2rem', marginBottom: '1rem', color: 'hsl(var(--danger))' }}>Erreur</h1>
        <p>Impossible de se connecter à l'API backend.</p>
      </div>
    );
  }

  const { date_maj, indices, volume_global, top_hausses, top_baisses } = summary;

  // Créer une map des prix actuels (ticker -> prix)
  const currentPrices: Record<string, number> = {};
  screener.forEach((s: any) => {
    currentPrices[s.ticker] = s.prix;
  });

  const renderTopList = (title: string, list: any[], isPositive: boolean) => (
    <Card className="animate-fade-in">
      <h3 style={{ marginBottom: '1.5rem', fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <span style={{ color: isPositive ? 'hsl(var(--success))' : 'hsl(var(--danger))' }}>{isPositive ? '↗' : '↘'}</span>
        {title}
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {list.map((item, idx) => (
          <div key={idx} style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            padding: '0.75rem',
            background: 'hsl(var(--bg-card-hover))',
            borderRadius: '8px',
            border: '1px solid hsl(var(--border-glass))'
          }}>
            <div>
              <Link href={`/actions/${item.ticker}`} style={{ fontWeight: 600, display: 'block' }}>
                {item.ticker}
              </Link>
              <span style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))' }}>
                {item.prix} FCFA
              </span>
            </div>
            <Badge value={item.variation} />
          </div>
        ))}
      </div>
    </Card>
  );

  return (
    <div className="animate-fade-in" style={{ maxWidth: '1200px', margin: '0 auto', paddingBottom: '4rem' }}>
      <MarketIndices 
        indices={indices} 
        volume={volume_global} 
        dateMaj={date_maj} 
      />

      {/* Analyse Sectorielle */}
      <SectorAnalysis data={sectorData} />

      {/* Alertes et Watchlist */}
      <WatchlistAlerts currentPrices={currentPrices} />

      {/* Section pleine-largeur pour les données Macro */}
      <MacroPanel />

      {/* Top hausses / baisses */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        {renderTopList('Top 5 des Hausses', top_hausses, true)}
        {renderTopList('Top 5 des Baisses', top_baisses, false)}
      </div>
    </div>
  );
}
