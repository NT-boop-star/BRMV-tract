import asyncio
import asyncpg
from datetime import date

DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "user": "brvm_user",
    "password": "brvm_password",
    "database": "brvm_tracker",
}

async def run():
    conn = await asyncpg.connect(**DB_CONFIG)
    print("Connexion OK")

    # 1. PAYS UEMOA
    pays = [
        ("Côte d'Ivoire", "CI"),
        ("Sénégal", "SN"),
        ("Burkina Faso", "BF"),
        ("Mali", "ML"),
        ("Bénin", "BJ"),
        ("Togo", "TG"),
        ("Niger", "NE"),
        ("Guinée-Bissau", "GW"),
        ("UEMOA (Global)", "UEMOA")
    ]
    
    for nom, code in pays:
        await conn.execute("INSERT INTO pays (nom, code) VALUES ($1, $2) ON CONFLICT (code) DO NOTHING", nom, code)
    
    rows = await conn.fetch("SELECT id, code FROM pays")
    pays_map = {r['code']: r['id'] for r in rows}

    # 2. INDICATEURS MACRO (Mockés pour 2024 basés sur les projections FMI/BCEAO)
    uemoa_id = pays_map.get("UEMOA")
    ci_id = pays_map.get("CI")
    sn_id = pays_map.get("SN")

    macros = [
        (uemoa_id, 2024, 6.5, 3.2, 28.5, 137000000),
        (ci_id, 2024, 6.8, 3.5, 32.0, 30000000),
        (sn_id, 2024, 8.3, 2.8, 29.0, 18000000),
    ]

    for m in macros:
        p_id, annee, crois, infla, banc, pop = m
        await conn.execute("""
            INSERT INTO indicateurs_macro (pays_id, annee, croissance_pib, inflation, taux_bancarisation, population)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT DO NOTHING
        """, p_id, annee, crois, infla, banc, pop)
        
    # 3. MATIERES PREMIERES
    matieres = [
        ("Cacao (Londres)", "COCOA", "USD/Tonne"),
        ("Pétrole Brent", "BRENT", "USD/Baril"),
        ("Or", "GOLD", "USD/Once")
    ]
    
    for nom, sym, uni in matieres:
        await conn.execute("INSERT INTO matieres_premieres (nom, symbole, unite) VALUES ($1, $2, $3) ON CONFLICT (symbole) DO NOTHING", nom, sym, uni)
        
    rows = await conn.fetch("SELECT id, symbole FROM matieres_premieres")
    mat_map = {r['symbole']: r['id'] for r in rows}
    
    # 4. PRIX MATIERES PREMIERES (Cours récents Avril 2026 / fin Mars)
    # Cacao s'est stabilisé autour de 8500 USD, Or à 2350 USD, Brent à 85 USD
    prix_data = [
        (date.today(), mat_map.get("COCOA"), 8450.00, 1.2),
        (date.today(), mat_map.get("BRENT"), 85.30, -0.5),
        (date.today(), mat_map.get("GOLD"), 2345.10, 0.8)
    ]
    
    for d, m_id, px, var in prix_data:
        if m_id:
            await conn.execute("""
                INSERT INTO prix_matieres_premieres (date_jour, matiere_id, prix, variation_jour)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (date_jour, matiere_id) DO UPDATE SET prix=EXCLUDED.prix, variation_jour=EXCLUDED.variation_jour
            """, d, m_id, px, var)
            
    print("Données Macro-économiques et Matières Premières insérées avec succès (Mocks temporaires).")
    await conn.close()

asyncio.run(run())
