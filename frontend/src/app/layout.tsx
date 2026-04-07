import type { Metadata } from 'next';
import Link from 'next/link';
import { Inter, Outfit } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });
const outfit = Outfit({ subsets: ['latin'], variable: '--font-outfit' });

export const metadata: Metadata = {
  title: 'BRVM Tracker Proxy',
  description: 'Analyse et suivi des actions de la Bourse Régionale des Valeurs Mobilières (BRVM)',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" className={`${inter.variable} ${outfit.variable}`}>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body>
        <div style={{ display: 'flex', minHeight: '100vh' }}>
          <aside className="glass-panel" style={{ width: '250px', margin: '16px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <span className="text-gradient" style={{ fontSize: '24px', fontWeight: 'bold' }}>B</span>
              <span style={{ fontSize: '18px', fontWeight: 'bold', fontFamily: 'var(--font-outfit)', color: 'hsl(var(--text-main))' }}>BRVM Tracker</span>
            </div>
            
            <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', padding: '0 1rem', flex: 1 }}>
              <Link href="/" style={{ padding: '0.75rem 1rem', borderRadius: '8px', display: 'flex', gap: '1rem', alignItems: 'center', color: 'hsl(var(--text-muted))', transition: 'background 0.2s, color 0.2s' }} className="hover-nav">
                <span>⌂</span>
                <span>Dashboard</span>
              </Link>
              <Link href="/screener" style={{ padding: '0.75rem 1rem', borderRadius: '8px', display: 'flex', gap: '1rem', alignItems: 'center', color: 'hsl(var(--text-muted))', transition: 'background 0.2s, color 0.2s' }} className="hover-nav">
                <span>🔍</span>
                <span>Screener</span>
              </Link>
              <Link href="/news" style={{ padding: '0.75rem 1rem', borderRadius: '8px', display: 'flex', gap: '1rem', alignItems: 'center', color: 'hsl(var(--text-muted))', transition: 'background 0.2s, color 0.2s' }} className="hover-nav">
                <span>📰</span>
                <span>Actualités</span>
              </Link>
            </nav>
            
            {/* Indicateur de status live (point vert) */}
            <div style={{ padding: '1.5rem', display: 'flex', alignItems: 'center', gap: '1rem', borderTop: '1px solid hsl(var(--border-glass))' }}>
              <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'hsl(var(--success))', boxShadow: '0 0 8px hsl(var(--success))' }}></div>
              <span style={{ fontSize: '0.8rem', color: 'hsl(var(--text-muted))' }}>Données Live API</span>
            </div>
          </aside>

          <main style={{ flex: 1, padding: '24px', overflowY: 'auto' }}>
            {children}
          </main>
        </div>
        <style dangerouslySetInnerHTML={{__html: `
          .hover-nav:hover {
            background: hsl(var(--accent-faded));
            color: hsl(var(--accent-primary)) !important;
          }
        `}} />
      </body>
    </html>
  );
}
