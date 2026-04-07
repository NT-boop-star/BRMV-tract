"""
Assigne le secteur d'activite officiel BRVM a chaque action.
"""
import asyncio
import asyncpg

DB_CONFIG = {
    "host": "localhost", "port": 5433,
    "user": "brvm_user", "password": "brvm_password",
    "database": "brvm_tracker",
}

TICKER_SECTEUR = {
    "BOAB": "Finance", "BOABF": "Finance", "BOAC": "Finance",
    "BOAM": "Finance", "BOAN":  "Finance", "BOAS": "Finance",
    "BICB": "Finance", "BICC":  "Finance", "BNBC": "Finance",
    "CBIBF":"Finance", "ECOC":  "Finance", "SGBC": "Finance",
    "SIBC": "Finance", "CABC":  "Finance", "ORGT": "Finance",
    "NSBC": "Finance", "SFCB":  "Finance", "ETIT": "Finance",
    "STAC": "Finance",
    "CFAC": "Distribution", "PRSC": "Distribution", "SDCC": "Distribution",
    "TTLC": "Distribution","TTLS": "Distribution", "UNLC": "Distribution",
    "UNXC": "Distribution",
    "PALC": "Agriculture", "SOGC": "Agriculture", "SAFC": "Agriculture",
    "SICC": "Agriculture",
    "FTSC": "Industrie", "NEIB": "Industrie", "NTLC": "Industrie",
    "SCBC": "Industrie", "SCRC": "Industrie", "SHEC": "Industrie",
    "SMBC": "Industrie", "SPHC": "Industrie", "STBC": "Industrie",
    "CIEC": "Industrie",
    "BOLC": "Transport", "SVOC": "Transport", "ABJC": "Transport",
    "SNTS": "Services Publics",
    "ORAC": "Télécommunications", "ONTBF": "Télécommunications",
}

SECTEURS = sorted(set(TICKER_SECTEUR.values())) + ["Autres Secteurs"]

async def run():
    conn = await asyncpg.connect(**DB_CONFIG)
    
    # 1. S'assurer que les secteurs officiels existent
    for nom in SECTEURS:
        await conn.execute(
            "INSERT INTO secteurs (nom) VALUES ($1) ON CONFLICT (nom) DO NOTHING", nom
        )
    
    rows = await conn.fetch("SELECT id, nom FROM secteurs")
    secteur_map = {r['nom']: r['id'] for r in rows}
    print("Secteurs:", secteur_map)
    
    # 2. Assigner les secteurs aux actions
    nb = 0
    for ticker, secteur_nom in TICKER_SECTEUR.items():
        sid = secteur_map.get(secteur_nom)
        result = await conn.execute(
            "UPDATE actions SET secteur_id = $1 WHERE ticker = $2", sid, ticker
        )
        if result == "UPDATE 1":
            nb += 1
            
    print(f"\n{nb} actions assignées à leur secteur")
    
    # 3. Les actions sans secteur -> Autres Secteurs
    autres_id = secteur_map.get("Autres Secteurs")
    result = await conn.execute(
        "UPDATE actions SET secteur_id = $1 WHERE secteur_id IS NULL", autres_id
    )
    print(f"Reste sans secteur -> Autres Secteurs : {result}")
    
    # 4. Recap
    recap = await conn.fetch("""
        SELECT s.nom, COUNT(a.id) as nb
        FROM secteurs s
        LEFT JOIN actions a ON s.id = a.secteur_id
        GROUP BY s.nom ORDER BY nb DESC
    """)
    print("\n=== REPARTITION FINALE ===")
    for r in recap:
        print(f"  {r['nom']}: {r['nb']} actions")
    
    await conn.close()
    print("\n[OK] Secteurs assignés avec succès !")

asyncio.run(run())
