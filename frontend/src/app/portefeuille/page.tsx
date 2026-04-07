export default function PortefeuillePage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header>
        <h1 className="prix-principal" style={{ margin: 0, fontSize: '2rem' }}>Portefeuille</h1>
        <p className="text-muted label-interface" style={{ marginTop: '0.5rem' }}>Suivi personnel de vos positions</p>
      </header>
      <div className="card">
        <p className="text-muted">Positions et performances en cours de construction...</p>
      </div>
    </div>
  );
}
