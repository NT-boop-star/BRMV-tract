"""Verification rapide des donnees en base TimescaleDB."""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import asyncio
import asyncpg

DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "user": "brvm_user",
    "password": "brvm_password",
    "database": "brvm_tracker",
}

async def verify():
    conn = await asyncpg.connect(**DB_CONFIG)

    # Compteurs
    tables = ["actions", "cotations", "indices", "cotations_indices", "seances", "logs_collecte"]
    print("== TABLES ==")
    for t in tables:
        n = await conn.fetchval(f"SELECT COUNT(*) FROM {t}")
        print(f"  {t:25s} : {n} lignes")

    # Echantillon cotations
    print("\n== 5 PREMIERES COTATIONS ==")
    rows = await conn.fetch("""
        SELECT a.ticker, c.prix, c.variation, c.volume
        FROM cotations c JOIN actions a ON c.action_id = a.id
        ORDER BY a.ticker LIMIT 5
    """)
    for r in rows:
        print(f"  {r['ticker']:8s} | {r['prix']:>8} FCFA | var: {r['variation']} | vol: {r['volume']}")

    # Indices
    print("\n== INDICES ==")
    rows = await conn.fetch("""
        SELECT i.nom, ci.valeur, ci.variation
        FROM cotations_indices ci JOIN indices i ON ci.indice_id = i.id
    """)
    for r in rows:
        print(f"  {r['nom']:20s} | {r['valeur']:>10} | {r['variation']}%")

    await conn.close()
    print("\n[OK] Verification terminee")

asyncio.run(verify())
