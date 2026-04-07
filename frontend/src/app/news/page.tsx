import { brvmAPI } from '@/lib/api';
import Link from 'next/link';

interface NewsItem {
  id: number;
  date_publication: string;
  titre: string;
  url: string;
  provenance: string | null;
  ticker: string | null;
  action_nom: string | null;
}

// Mapper les sources vers des couleurs distinctives
function getSourceColor(provenance: string | null): string {
  if (!provenance) return 'hsl(var(--text-muted))';
  const map: Record<string, string> = {
    'richbourse': 'hsl(var(--accent-primary))',
    'brvm': 'hsl(var(--success))',
    'sikafinance': 'hsl(47 95% 55%)', // amber/gold
  };
  return map[provenance.toLowerCase()] ?? 'hsl(var(--text-muted))';
}

function formatRelativeDate(isoDate: string): string {
  if (!isoDate) return '';
  const d = new Date(isoDate);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffH = Math.floor(diffMs / (1000 * 60 * 60));
  const diffD = Math.floor(diffH / 24);
  if (diffD > 30) return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' });
  if (diffD > 0) return `il y a ${diffD}j`;
  if (diffH > 0) return `il y a ${diffH}h`;
  return 'Aujourd\'hui';
}

export default async function NewsPage({ searchParams }: { searchParams?: Promise<{ [key: string]: string | string[] | undefined }> }) {
  const resolvedParams = searchParams ? await searchParams : {};
  const pageStr = resolvedParams.page;
  const page = typeof pageStr === 'string' ? parseInt(pageStr, 10) : 1;
  const limit = 20;
  const offset = (page >= 1 ? page - 1 : 0) * limit;

  let newsList: NewsItem[] = [];
  try {
    newsList = await brvmAPI.getMarketNews(limit, offset);
  } catch {
    return (
      <div className="animate-fade-in" style={{ maxWidth: '900px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '2rem', color: 'hsl(var(--danger))' }}>Erreur</h1>
        <p>Impossible de charger le flux d'actualités.</p>
      </div>
    );
  }

  // Grouper par date du jour
  const grouped: Record<string, NewsItem[]> = {};
  for (const item of newsList) {
    if (!item.date_publication) continue;
    const dateKey = new Date(item.date_publication).toLocaleDateString('fr-FR', {
      weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
    });
    if (!grouped[dateKey]) grouped[dateKey] = [];
    grouped[dateKey].push(item);
  }

  const isEmpty = newsList.length === 0;

  return (
    <div className="animate-fade-in" style={{ maxWidth: '900px', margin: '0 auto' }}>
      {/* Header */}
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Actualités du Marché</h1>
        <p style={{ color: 'hsl(var(--text-muted))' }}>
          Flux consolidé de {newsList.length} articles · Sources&nbsp;:&nbsp;
          <span style={{ color: 'hsl(var(--accent-primary))' }}>Richbourse</span>,&nbsp;
          <span style={{ color: 'hsl(47 95% 55%)' }}>Sikafinance</span>,&nbsp;
          <span style={{ color: 'hsl(var(--success))' }}>BRVM</span>
        </p>
      </div>

      {isEmpty ? (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'hsl(var(--text-muted))' }}>
          <p style={{ fontSize: '3rem', marginBottom: '1rem' }}>📭</p>
          <p>Aucune actualité disponible pour le moment.</p>
          <p style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>Relancez le pipeline de collecte pour alimenter cette vue.</p>
        </div>
      ) : (
        Object.entries(grouped).map(([dateKey, items]) => (
          <div key={dateKey} style={{ marginBottom: '2.5rem' }}>
            {/* Date separator */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1.25rem' }}>
              <div style={{ flex: 1, height: '1px', background: 'hsl(var(--border-glass))' }} />
              <span style={{ fontSize: '0.8rem', color: 'hsl(var(--text-muted))', whiteSpace: 'nowrap', textTransform: 'capitalize' }}>
                {dateKey}
              </span>
              <div style={{ flex: 1, height: '1px', background: 'hsl(var(--border-glass))' }} />
            </div>

            {/* News cards */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {items.map((item) => (
                <div
                  key={item.id}
                  className="glass-panel"
                  style={{
                    display: 'block',
                    padding: '1.25rem 1.5rem',
                    transition: 'border-color 0.2s, background 0.2s',
                    borderColor: 'hsl(var(--border-glass))',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem' }}>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <a href={item.url} target="_blank" rel="noopener noreferrer" style={{ textDecoration: 'none' }}>
                        <p style={{
                          fontWeight: 500,
                          color: 'hsl(var(--text-main))',
                          lineHeight: 1.4,
                          overflow: 'hidden',
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          transition: 'color 0.2s'
                        }}>
                          {item.titre}
                        </p>
                      </a>

                      {/* Meta row */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '0.75rem', flexWrap: 'wrap' }}>
                        {/* Source badge */}
                        {item.provenance && (
                          <span style={{
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            color: getSourceColor(item.provenance),
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em',
                          }}>
                            {item.provenance}
                          </span>
                        )}

                        {/* Ticker tag */}
                        {item.ticker && (
                          <Link
                            href={`/actions/${item.ticker}`}
                            style={{
                              fontSize: '0.75rem',
                              fontWeight: 600,
                              color: 'hsl(var(--text-main))',
                              backgroundColor: 'hsl(var(--accent-faded))',
                              border: '1px solid hsl(var(--accent-primary) / 0.3)',
                              padding: '0.125rem 0.5rem',
                              borderRadius: '4px',
                              textDecoration: 'none'
                            }}
                          >
                            {item.ticker}
                          </Link>
                        )}
                      </div>
                    </div>

                    {/* Date relative */}
                    <span style={{
                      fontSize: '0.75rem',
                      color: 'hsl(var(--text-muted))',
                      whiteSpace: 'nowrap',
                      marginTop: '0.125rem',
                      flexShrink: 0,
                    }}>
                      {formatRelativeDate(item.date_publication)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))
      )}
      {/* Pagination Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '2rem', paddingTop: '1rem', borderTop: '1px solid hsl(var(--border-glass))' }}>
        <Link 
          href={`/news?page=${Math.max(1, page - 1)}`}
          style={{ 
            padding: '0.5rem 1rem', 
            borderRadius: '6px', 
            background: 'hsl(var(--surface-light))', 
            color: page > 1 ? 'hsl(var(--text-main))' : 'hsl(var(--text-muted))',
            pointerEvents: page > 1 ? 'auto' : 'none',
            textDecoration: 'none'
          }}
        >
          ← Précédent
        </Link>
        <span style={{ color: 'hsl(var(--text-muted))' }}>Page {page}</span>
        <Link 
          href={`/news?page=${page + 1}`}
          style={{ 
            padding: '0.5rem 1rem', 
            borderRadius: '6px', 
            background: 'hsl(var(--surface-light))', 
            color: newsList.length === limit ? 'hsl(var(--text-main))' : 'hsl(var(--text-muted))',
            pointerEvents: newsList.length === limit ? 'auto' : 'none',
            textDecoration: 'none'
          }}
        >
          Suivant →
        </Link>
      </div>
    </div>
  );
}
