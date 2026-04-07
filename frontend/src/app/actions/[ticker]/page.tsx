import { brvmAPI } from '@/lib/api';
import { ActionHeader } from '@/components/actions/ActionHeader';
import { StockChart } from '@/components/actions/StockChart';
import { DividendsList } from '@/components/actions/DividendsList';
import { DividendsHistory } from '@/components/actions/DividendsHistory';
import { NotationsNews } from '@/components/actions/NotationsNews';
import Link from 'next/link';

export default async function ActionPage({ params }: { params: Promise<{ ticker: string }> }) {
  const resolvedParams = await params;
  const { ticker } = resolvedParams;

  let details;
  let chartData;

  try {
    const tickerUpper = ticker.toUpperCase();
    // Requetes en parallele pour de meilleures performances (On recupere tout l'historique)
    const [detailsRes, chartRes] = await Promise.all([
      brvmAPI.getActionDetails(tickerUpper),
      brvmAPI.getActionChart(tickerUpper)   // tout l'historique depuis 2000
    ]);
    details = detailsRes;
    chartData = chartRes;
  } catch (error) {
    return (
      <div className="animate-fade-in" style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Link href="/screener" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', marginBottom: '2rem', color: 'hsl(var(--text-muted))' }}>
          <span>← Retour au Screener</span>
        </Link>
        <h1 style={{ fontSize: '2rem', marginBottom: '1rem', color: 'hsl(var(--danger))' }}>Erreur</h1>
        <p>Impossible de trouver l'action {ticker.toUpperCase()}.</p>
      </div>
    );
  }

  return (
    <div className="animate-fade-in" style={{ maxWidth: '1200px', margin: '0 auto' }}>
      <Link href="/screener" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', color: 'hsl(var(--text-muted))' }}>
        <span>← Retour au Screener</span>
      </Link>

      <ActionHeader 
        ticker={details.action.ticker}
        nom={details.action.nom}
        secteur={details.action.secteur?.nom}
        prix={details.derniere_cotation?.prix}
        variation={details.derniere_cotation?.variation}
      />

      {/* Graphique pleine largeur */}
      <StockChart data={chartData} />

      {/* Grid en-dessous : infos (gauche) + publications / notations (droite) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '1.5rem', marginTop: '1.5rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <DividendsList dividendes={details.dividendes} />
          <DividendsHistory dividends={details.dividendes} />
        </div>
        <div>
          <NotationsNews notations={details.notations} news={details.news} rapports_annuels={details.rapports_annuels} defaultTab="finances" />
        </div>
      </div>
    </div>
  );
}
