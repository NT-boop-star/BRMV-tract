export default function IAPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header>
        <h1 className="prix-principal text-purple" style={{ margin: 0, fontSize: '2rem' }}>Assistant IA</h1>
        <p className="text-muted label-interface" style={{ marginTop: '0.5rem' }}>Analyse cognitive par Gemini 2.0</p>
      </header>
      <div className="card">
        <p className="text-muted">Quiz et interface conversationnelle en cours de construction...</p>
      </div>
    </div>
  );
}
