export default function MarchesPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header>
        <h1 className="prix-principal" style={{ margin: 0, fontSize: '2rem' }}>Marchés</h1>
        <p className="text-muted label-interface" style={{ marginTop: '0.5rem' }}>Vue d'ensemble des cotations de la BRVM</p>
      </header>
      <div className="card">
        <p className="text-muted">Tableau des cotations en cours de construction...</p>
      </div>
    </div>
  );
}
