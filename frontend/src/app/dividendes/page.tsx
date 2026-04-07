export default function DividendesPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header>
        <h1 className="prix-principal" style={{ margin: 0, fontSize: '2rem' }}>Dividendes</h1>
        <p className="text-muted label-interface" style={{ marginTop: '0.5rem' }}>Calendrier et historique des détachements</p>
      </header>
      <div className="card">
        <p className="text-muted">Tableau des dividendes en cours de construction...</p>
      </div>
    </div>
  );
}
