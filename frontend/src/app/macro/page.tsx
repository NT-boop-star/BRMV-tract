export default function MacroPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header>
        <h1 className="prix-principal" style={{ margin: 0, fontSize: '2rem' }}>Macroéconomie UEMOA</h1>
        <p className="text-muted label-interface" style={{ marginTop: '0.5rem' }}>Indicateurs fondamentaux régionaux</p>
      </header>
      <div className="card">
        <p className="text-muted">Données Banque Mondiale et BCEAO en cours de construction...</p>
      </div>
    </div>
  );
}
