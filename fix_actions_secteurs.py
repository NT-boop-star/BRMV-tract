"""
Script de re-insertion des donnees BRVM depuis le JSON existant
et assignation des secteurs d'activite officiels.
"""
import asyncio
import asyncpg

DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "user": "brvm_user",
    "password": "brvm_password",
    "database": "brvm_tracker",
}

# Secteurs officiels BRVM -> mapping ticker
TICKER_SECTEUR = {
    # Finance
    "BOAB":  "Finance", "BOABF": "Finance", "BOAC": "Finance",
    "BOAM":  "Finance", "BOAN":  "Finance", "BOAS": "Finance",
    "BICB":  "Finance", "BICC":  "Finance", "BNBC": "Finance",
    "CBIBF": "Finance", "ECOC":  "Finance", "SGBC": "Finance",
    "SIBC":  "Finance", "CABC":  "Finance", "ORGT": "Finance",
    "NSBC":  "Finance", "SFCB":  "Finance", "ETIT": "Finance",
    "STAC":  "Finance",
    # Distribution
    "CFAC": "Distribution", "PRSC":  "Distribution", "SDCC": "Distribution",
    "TTLC": "Distribution", "TTLS":  "Distribution", "UNLC": "Distribution",
    "UNXC": "Distribution",
    # Agriculture
    "PALC": "Agriculture", "SOGC": "Agriculture", "SAFC": "Agriculture",
    "SICC": "Agriculture",
    # Industrie
    "FTSC": "Industrie", "NEIB": "Industrie", "NTLC": "Industrie",
    "SCBC": "Industrie", "SCRC": "Industrie", "SHEC": "Industrie",
    "SMBC": "Industrie", "SPHC": "Industrie", "STBC": "Industrie",
    "CIEC": "Industrie",
    # Transport
    "BOLC": "Transport", "SVOC": "Transport", "ABJC": "Transport",
    # Services Publics
    "SNTS": "Services Publics",
    # Télécommunications
    "ORAC": "Télécommunications", "ONTBF": "Télécommunications",
}

SECTEURS = sorted(set(TICKER_SECTEUR.values()))

async def run():
    conn = await asyncpg.connect(**DB_CONFIG)
    print("[DB] Connexion OK")

    # 1. Insérer les secteurs officiels
    print("\n[1/3] Insertion des secteurs BRVM...")
    for nom in SECTEURS:
        await conn.execute(
            "INSERT INTO secteurs (nom) VALUES ($1) ON CONFLICT (nom) DO NOTHING",
            nom
        )
    print(f"     {len(SECTEURS)} secteurs prêts")

    # 2. Récupérer les IDs secteurs
    rows = await conn.fetch("SELECT id, nom FROM secteurs")
    secteur_map = {r['nom']: r['id'] for r in rows}

    # 3. Lire les tickers depuis les cotations existantes
    print("\n[2/3] Récupération des tickers depuis les cotations...")
    cot_tickers = await conn.fetch("""
        SELECT DISTINCT a.ticker, a.nom FROM actions a
        UNION
        SELECT DISTINCT cot.ticker, cot.ticker FROM (
            SELECT DISTINCT ON (action_id) action_id FROM cotations
        ) AS sub
        JOIN actions a ON sub.action_id = a.id
    """)
    
    # Si pas d'actions, lire depuis le JSON
    import json, os
    json_path = os.path.join(os.path.dirname(__file__), "scraper", "brvm_data.json")
    with open(json_path, "r", encoding="utf-8") as f:
        brvm_data = json.load(f)
    
    cotations = brvm_data.get("cotations", [])
    print(f"     {len(cotations)} cotations trouvées dans le JSON")
    
    # 3a. Insérer les actions depuis le JSON
    print("\n[3/3] Insertion des actions et assignation des secteurs...")
    nb_inserted = 0
    nb_sector_assigned = 0
    for cot in cotations:
        ticker = cot.get("ticker", "").strip()
        nom = cot.get("nom", ticker)
        secteur_nom = TICKER_SECTEUR.get(ticker, "Autres Secteurs")
        secteur_id = secteur_map.get(secteur_nom)
        
        await conn.execute("""
            INSERT INTO actions (ticker, nom, secteur_id)
            VALUES ($1, $2, $3)
            ON CONFLICT (ticker) DO UPDATE SET 
                nom = EXCLUDED.nom,
                secteur_id = EXCLUDED.secteur_id
        """, ticker, nom, secteur_id)
        nb_inserted += 1
        if secteur_id:
            nb_sector_assigned += 1
    
    print(f"     {nb_inserted} actions insérées / mises à jour")
    print(f"     {nb_sector_assigned} actions associées à un secteur")
    
    # Récap final
    recap = await conn.fetch("""
        SELECT s.nom as secteur, COUNT(a.id) as nb
        FROM secteurs s
        LEFT JOIN actions a ON s.id = a.secteur_id
        GROUP BY s.nom ORDER BY nb DESC
    """)
    print("\n--- RECAP SECTEURS ---")
    for r in recap:
        print(f"  {r['secteur']}: {r['nb']} actions")

    await conn.close()
    print("\n[OK] Terminé !")

asyncio.run(run())
