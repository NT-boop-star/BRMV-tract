"""
Script de correction des secteurs BRVM.
1. Supprime les faux secteurs (noms d'entreprises).
2. Insère les vrais secteurs d'activité BRVM.
3. Associe chaque action à son secteur.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://brvm_user:brvm_password@localhost:5433/brvm_tracker"

# Secteurs officiels BRVM
SECTEURS = [
    "Finance",
    "Distribution",
    "Agriculture",
    "Industrie",
    "Transport",
    "Services Publics",
    "Autres Secteurs",
    "Télécommunications",
]

# Mapping ticker -> secteur (classification BRVM officielle)
TICKER_SECTEUR = {
    # Finance / Banques
    "BOAB":  "Finance",
    "BOABF": "Finance",
    "BOAC":  "Finance",
    "BOAM":  "Finance",
    "BOAN":  "Finance",
    "BOAS":  "Finance",
    "BICB":  "Finance",
    "BICC":  "Finance",
    "BNBC":  "Finance",
    "CBIBF": "Finance",
    "ECOC":  "Finance",
    "SGBC":  "Finance",
    "SIBC":  "Finance",
    "CABC":  "Finance",
    "ORGT":  "Finance",
    "NSBC":  "Finance",
    "SFCB":  "Finance",  # SAFCA
    "ETIT":  "Finance",  # ETI
    "STAC":  "Finance",  # STAC microfinance
    
    # Distribution
    "CFAC":  "Distribution",
    "PRSC":  "Distribution",
    "SDCC":  "Distribution",
    "TTLC":  "Distribution",
    "TTLS":  "Distribution",
    "UNLC":  "Distribution",
    "UNXC":  "Distribution",

    # Agriculture
    "PALC":  "Agriculture",
    "SOGC":  "Agriculture",
    "SAFC":  "Agriculture",
    "SICC":  "Agriculture",

    # Industrie
    "ABJC":  "Industrie",
    "CIEC":  "Industrie",
    "FTSC":  "Industrie",
    "NEIB":  "Industrie",
    "NTLC":  "Industrie",
    "SCBC":  "Industrie",
    "SCRC":  "Industrie",
    "SHEC":  "Industrie",
    "SMBC":  "Industrie",
    "SPHC":  "Industrie",
    "STBC":  "Industrie",

    # Transport
    "ABJC":  "Transport",
    "BOLC":  "Transport",
    "SVOC":  "Transport",

    # Services Publics
    "CIEC":  "Services Publics",
    "SNTS":  "Services Publics",
    "SDCC":  "Services Publics",

    # Télécommunications
    "ORAC":  "Télécommunications",
    "ONTBF": "Télécommunications",

    # Autres
    "ABJC":  "Autres Secteurs",
}

# Classification finale propre (priorité aux secteurs clés)
TICKER_SECTEUR_FINAL = {
    "BOAB":  "Finance",
    "BOABF": "Finance",
    "BOAC":  "Finance",
    "BOAM":  "Finance",
    "BOAN":  "Finance",
    "BOAS":  "Finance",
    "BICB":  "Finance",
    "BICC":  "Finance",
    "BNBC":  "Finance",
    "CBIBF": "Finance",
    "ECOC":  "Finance",
    "SGBC":  "Finance",
    "SIBC":  "Finance",
    "CABC":  "Finance",
    "ORGT":  "Finance",
    "NSBC":  "Finance",
    "SFCB":  "Finance",
    "ETIT":  "Finance",
    "STAC":  "Finance",
    "CFAC":  "Distribution",
    "PRSC":  "Distribution",
    "SDCC":  "Distribution",
    "TTLC":  "Distribution",
    "TTLS":  "Distribution",
    "UNLC":  "Distribution",
    "UNXC":  "Distribution",
    "PALC":  "Agriculture",
    "SOGC":  "Agriculture",
    "SAFC":  "Agriculture",
    "SICC":  "Agriculture",
    "FTSC":  "Industrie",
    "NEIB":  "Industrie",
    "NTLC":  "Industrie",
    "SCBC":  "Industrie",
    "SCRC":  "Industrie",
    "SHEC":  "Industrie",
    "SMBC":  "Industrie",
    "SPHC":  "Industrie",
    "STBC":  "Industrie",
    "CIEC":  "Industrie",
    "BOLC":  "Transport",
    "SVOC":  "Transport",
    "ABJC":  "Transport",
    "SNTS":  "Services Publics",
    "ORAC":  "Télécommunications",
    "ONTBF": "Télécommunications",
}

async def fix_secteurs():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        # 1. Vider la table secteurs
        print("[1/4] Nettoyage de la table secteurs...")
        await conn.execute(text("UPDATE actions SET secteur_id = NULL"))
        await conn.execute(text("TRUNCATE secteurs RESTART IDENTITY CASCADE"))
        print("     OK")

        # 2. Insérer les vrais secteurs
        print("[2/4] Insertion des secteurs officiels BRVM...")
        for nom in SECTEURS:
            await conn.execute(text("INSERT INTO secteurs (nom) VALUES (:nom) ON CONFLICT DO NOTHING"), {"nom": nom})
        print(f"     {len(SECTEURS)} secteurs inseres")

        # 3. Récupérer les IDs des secteurs
        result = await conn.execute(text("SELECT id, nom FROM secteurs"))
        secteur_map = {row.nom: row.id for row in result.fetchall()}
        print(f"     Mapping: {secteur_map}")

        # 4. Associer chaque action à son secteur
        print("[3/4] Association des actions à leurs secteurs...")
        nb_updated = 0
        for ticker, secteur_nom in TICKER_SECTEUR_FINAL.items():
            sid = secteur_map.get(secteur_nom)
            if sid:
                res = await conn.execute(
                    text("UPDATE actions SET secteur_id = :sid WHERE ticker = :ticker"),
                    {"sid": sid, "ticker": ticker}
                )
                if res.rowcount > 0:
                    nb_updated += 1
        print(f"     {nb_updated} actions mises a jour")

        # 5. Vérification
        print("[4/4] Vérification...")
        result = await conn.execute(text("""
            SELECT s.nom as secteur, COUNT(a.id) as nb
            FROM secteurs s
            LEFT JOIN actions a ON s.id = a.secteur_id
            GROUP BY s.nom
            ORDER BY nb DESC
        """))
        for row in result.fetchall():
            print(f"     {row.secteur}: {row.nb} actions")

    print("\n[OK] Migration des secteurs terminee !")
    await engine.dispose()

asyncio.run(fix_secteurs())
