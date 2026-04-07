'use client';

import React, { useState } from 'react';
import { Card } from '../ui/Card';

interface Notation {
  agence: string;
  date_notation?: string;
  note_long_terme?: string;
  note_court_terme?: string;
}

interface NewsItem {
  date_publication: string;
  titre: string;
  url: string;
  provenance?: string;
}

interface RapportAnnuel {
  annee: number;
  ca?: number;
  resultat_net?: number;
  capitaux_propres?: number;
  dette_nette?: number;
  ebitda?: number;
  flux_exploitation?: number;
  capex?: number;
  fcf?: number;
}

interface NotationsNewsProps {
  notations: Notation[];
  news?: NewsItem[];
  rapports_annuels?: RapportAnnuel[];
  defaultTab?: 'notations' | 'publications' | 'finances';
}

const getRatingColor = (note?: string) => {
  if (!note) return 'hsl(var(--text-muted))';
  const n = note.toUpperCase();
  if (n.startsWith('A')) return '#22c55e';
  if (n.startsWith('B')) return '#f59e0b';
  if (n.startsWith('C')) return '#ef4444';
  return 'hsl(var(--accent-primary))';
};

export function NotationsNews({ notations, news = [], rapports_annuels = [], defaultTab = 'notations' }: NotationsNewsProps) {
  const [activeTab, setActiveTab] = useState<'notations' | 'publications' | 'finances'>(defaultTab);
  const [newsPage, setNewsPage] = useState(0);
  const NEWS_PER_PAGE = 20;

  const sortedNews = [...news].sort((a, b) =>
    new Date(b.date_publication).getTime() - new Date(a.date_publication).getTime()
  );
  const totalNewsPages = Math.ceil(sortedNews.length / NEWS_PER_PAGE);
  const pagedNews = sortedNews.slice(newsPage * NEWS_PER_PAGE, (newsPage + 1) * NEWS_PER_PAGE);

  const tabStyle = (tab: 'notations' | 'publications' | 'finances'): React.CSSProperties => ({
    padding: '0.4rem 0.875rem',
    borderRadius: '8px',
    fontSize: '0.875rem',
    fontWeight: 600,
    cursor: 'pointer',
    border: '1px solid',
    transition: 'all 0.15s ease',
    borderColor: activeTab === tab ? 'hsl(var(--accent-primary))' : 'transparent',
    backgroundColor: activeTab === tab ? 'hsl(var(--accent-primary) / 0.15)' : 'transparent',
    color: activeTab === tab ? 'hsl(var(--accent-primary))' : 'hsl(var(--text-muted))',
  });

  return (
    <Card style={{ display: 'flex', flexDirection: 'column', minHeight: '400px' }}>
      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem', flexShrink: 0 }}>
        <button style={tabStyle('notations')} onClick={() => setActiveTab('notations')}>
          Notations {notations.length > 0 && <span style={{ opacity: 0.7, fontWeight: 400 }}>({notations.length})</span>}
        </button>
        <button style={tabStyle('publications')} onClick={() => { setActiveTab('publications'); setNewsPage(0); }}>
          Publications {news.length > 0 && <span style={{ opacity: 0.7, fontWeight: 400 }}>({news.length})</span>}
        </button>
        <button style={tabStyle('finances')} onClick={() => setActiveTab('finances')}>
          États Financiers {rapports_annuels.length > 0 && <span style={{ opacity: 0.7, fontWeight: 400 }}>({rapports_annuels.length})</span>}
        </button>
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflowY: 'auto', minHeight: 0 }}>

        {/* === NOTATIONS === */}
        {activeTab === 'notations' && (
          <>
            {notations.length === 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '0.5rem' }}>
                <span style={{ fontSize: '2rem' }}>📊</span>
                <p style={{ color: 'hsl(var(--text-muted))', textAlign: 'center', fontSize: '0.875rem' }}>
                  Aucune notation financière disponible pour cette entreprise.
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem' }}>
                {notations.map((note, idx) => (
                  <div key={idx} style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.05)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                      <div>
                        <p style={{ fontWeight: 700, fontSize: '0.95rem' }}>{note.agence}</p>
                        {note.date_notation && (
                          <p style={{ fontSize: '0.75rem', color: 'hsl(var(--text-muted))', marginTop: '0.15rem' }}>{note.date_notation}</p>
                        )}
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '0.75rem' }}>
                      {note.note_long_terme && (
                        <div style={{ textAlign: 'center', padding: '0.5rem', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                          <p style={{ fontSize: '0.7rem', color: 'hsl(var(--text-muted))', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Long Terme</p>
                          <p style={{ fontWeight: 800, fontSize: '1.1rem', color: getRatingColor(note.note_long_terme) }}>{note.note_long_terme}</p>
                        </div>
                      )}
                      {note.note_court_terme && (
                        <div style={{ textAlign: 'center', padding: '0.5rem', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                          <p style={{ fontSize: '0.7rem', color: 'hsl(var(--text-muted))', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Court Terme</p>
                          <p style={{ fontWeight: 800, fontSize: '1.1rem', color: getRatingColor(note.note_court_terme) }}>{note.note_court_terme}</p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* === PUBLICATIONS === */}
        {activeTab === 'publications' && (
          <>
            {sortedNews.length === 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', gap: '0.5rem' }}>
                <span style={{ fontSize: '2rem' }}>📰</span>
                <p style={{ color: 'hsl(var(--text-muted))', textAlign: 'center', fontSize: '0.875rem' }}>
                  Aucune publication officielle liée à cette entreprise.
                </p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.625rem' }}>
                {pagedNews.map((item, idx) => (
                  <a
                    key={idx}
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: 'block',
                      padding: '0.75rem',
                      backgroundColor: 'rgba(255,255,255,0.03)',
                      border: '1px solid rgba(255,255,255,0.06)',
                      borderRadius: '8px',
                      textDecoration: 'none',
                      transition: 'border-color 0.15s, background 0.15s',
                    }}
                    onMouseEnter={e => {
                      (e.currentTarget as HTMLAnchorElement).style.borderColor = 'rgba(149,108,255,0.4)';
                      (e.currentTarget as HTMLAnchorElement).style.backgroundColor = 'rgba(149,108,255,0.06)';
                    }}
                    onMouseLeave={e => {
                      (e.currentTarget as HTMLAnchorElement).style.borderColor = 'rgba(255,255,255,0.06)';
                      (e.currentTarget as HTMLAnchorElement).style.backgroundColor = 'rgba(255,255,255,0.03)';
                    }}
                  >
                    <p style={{ fontSize: '0.8rem', color: 'hsl(var(--text-muted))', marginBottom: '0.25rem' }}>
                      {new Date(item.date_publication).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })}
                      {item.provenance && <span style={{ marginLeft: '0.5rem', opacity: 0.6 }}>· {item.provenance}</span>}
                    </p>
                    <p style={{ fontSize: '0.85rem', color: 'hsl(var(--text-main))', lineHeight: 1.4, fontWeight: 500 }}>{item.titre}</p>
                  </a>
                ))}

                {totalNewsPages > 1 && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                    <button
                      onClick={() => setNewsPage(p => Math.max(0, p - 1))}
                      disabled={newsPage === 0}
                      style={{ padding: '0.35rem 0.75rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(255,255,255,0.04)', color: newsPage === 0 ? 'hsl(var(--text-muted))' : 'hsl(var(--text-main))', cursor: newsPage === 0 ? 'not-allowed' : 'pointer', fontSize: '0.8rem' }}
                    >← Préc.</button>
                    <span style={{ fontSize: '0.8rem', color: 'hsl(var(--text-muted))' }}>
                      Page {newsPage + 1} / {totalNewsPages} · {sortedNews.length} publications
                    </span>
                    <button
                      onClick={() => setNewsPage(p => Math.min(totalNewsPages - 1, p + 1))}
                      disabled={newsPage >= totalNewsPages - 1}
                      style={{ padding: '0.35rem 0.75rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(255,255,255,0.04)', color: newsPage >= totalNewsPages - 1 ? 'hsl(var(--text-muted))' : 'hsl(var(--text-main))', cursor: newsPage >= totalNewsPages - 1 ? 'not-allowed' : 'pointer', fontSize: '0.8rem' }}
                    >Suiv. →</button>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* === ETATS FINANCIERS === */}
        {activeTab === 'finances' && (
          <div style={{ overflowX: 'auto', paddingBottom: '1rem' }}>
            {rapports_annuels.length === 0 ? (
              <p style={{ color: 'hsl(var(--text-muted))', fontSize: '0.875rem' }}>Aucun état financier disponible.</p>
            ) : (
              <table style={{ width: '100%', fontSize: '0.875rem', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ color: 'hsl(var(--text-muted))', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <th style={{ textAlign: 'left', padding: '0.75rem' }}>Année</th>
                    <th style={{ textAlign: 'right', padding: '0.75rem' }}>Chiffre d&apos;Affaires</th>
                    <th style={{ textAlign: 'right', padding: '0.75rem' }}>Résultat Net</th>
                    <th style={{ textAlign: 'right', padding: '0.75rem' }}>FCF</th>
                  </tr>
                </thead>
                <tbody>
                  {rapports_annuels.map((r, i) => (
                    <tr key={i} style={{ borderBottom: i === rapports_annuels.length - 1 ? 'none' : '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '0.75rem', fontWeight: 600 }}>{r.annee}</td>
                      <td style={{ padding: '0.75rem', textAlign: 'right' }}>{r.ca ? new Intl.NumberFormat('fr-FR').format(r.ca) + ' FCFA' : '-'}</td>
                      <td style={{ padding: '0.75rem', textAlign: 'right', color: r.resultat_net && r.resultat_net > 0 ? '#22c55e' : '#ef4444' }}>
                        {r.resultat_net ? new Intl.NumberFormat('fr-FR').format(r.resultat_net) + ' FCFA' : '-'}
                      </td>
                      <td style={{ padding: '0.75rem', textAlign: 'right' }}>{r.fcf ? new Intl.NumberFormat('fr-FR').format(r.fcf) + ' FCFA' : '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

      </div>
    </Card>
  );
}
