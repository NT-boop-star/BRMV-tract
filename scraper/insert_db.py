"""
Script d'insertion des donnees BRVM scrappees dans TimescaleDB.
Lit brvm_data.json et insere dans :
  - actions (table de reference)
  - indices (table de reference)
  - cotations (hypertable)
  - cotations_indices (hypertable)
"""
import sys
import io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import asyncio
import json
import asyncpg
from datetime import date as dt_date
from decimal import Decimal

# Configuration DB (port 5433 = Docker TimescaleDB)
DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "user": "brvm_user",
    "password": "brvm_password",
    "database": "brvm_tracker",
}


async def insert_brvm_data():
    """Insere les donnees scrappees dans la base TimescaleDB."""

    # 1. Charger les donnees JSON
    with open("brvm_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    cotations_data = data.get("cotations", [])
    indices_data = data.get("indices", [])
    caps_data = data.get("capitalisations", {})

    print(f"[DB] Donnees a inserer : {len(cotations_data)} cotations, {len(indices_data)} indices")

    # 2. Connexion a la base
    conn = await asyncpg.connect(**DB_CONFIG)
    print("[DB] Connexion a TimescaleDB etablie")

    try:
        # =============================================
        # ETAPE A : Inserer les actions (upsert ticker)
        # =============================================
        print("[DB] Insertion des actions...")
        actions_inserees = 0
        for cot in cotations_data:
            ticker = cot["ticker"]
            nom = cot["nom"]
            await conn.execute("""
                INSERT INTO actions (ticker, nom)
                VALUES ($1, $2)
                ON CONFLICT (ticker) DO UPDATE SET nom = EXCLUDED.nom
            """, ticker, nom)
            actions_inserees += 1

        print(f"[DB] {actions_inserees} actions inserees/mises a jour")

        # =============================================
        # ETAPE B : Inserer les indices de reference
        # =============================================
        print("[DB] Insertion des indices de reference...")
        index_map = {
            "BRVM Composite": "Indice composite regroupant toutes les actions BRVM",
            "BRVM 30": "Indice des 30 valeurs les plus actives",
            "BRVM Prestige": "Indice des valeurs prestige de la BRVM",
        }
        for idx in indices_data:
            nom = idx["nom"]
            desc = index_map.get(nom, "")
            await conn.execute("""
                INSERT INTO indices (nom, description)
                VALUES ($1, $2)
                ON CONFLICT (nom) DO NOTHING
            """, nom, desc)

        print(f"[DB] {len(indices_data)} indices de reference inseres")

        # =============================================
        # ETAPE C : Inserer les cotations (hypertable)
        # =============================================
        print("[DB] Insertion des cotations...")
        cotations_inserees = 0
        for cot in cotations_data:
            # Recuperer l'action_id depuis le ticker
            action_id = await conn.fetchval(
                "SELECT id FROM actions WHERE ticker = $1", cot["ticker"]
            )
            if action_id is None:
                print(f"  [WARN] Ticker {cot['ticker']} non trouve dans actions")
                continue

            prix = cot["cours_cloture"] if cot["cours_cloture"] is not None else 0
            variation = Decimal(str(cot["variation"])) if cot["variation"] is not None else None
            volume = cot["volume"]
            date_seance = dt_date.fromisoformat(cot["date_seance"])

            await conn.execute("""
                INSERT INTO cotations (date_seance, action_id, prix, variation, volume)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (date_seance, action_id) DO UPDATE
                SET prix = EXCLUDED.prix, variation = EXCLUDED.variation, volume = EXCLUDED.volume
            """, date_seance, action_id, prix, variation, volume)
            cotations_inserees += 1

        print(f"[DB] {cotations_inserees} cotations inserees")

        # =============================================
        # ETAPE D : Inserer les cotations des indices
        # =============================================
        print("[DB] Insertion des cotations indices...")
        indices_inseres = 0
        for idx in indices_data:
            indice_id = await conn.fetchval(
                "SELECT id FROM indices WHERE nom = $1", idx["nom"]
            )
            if indice_id is None:
                print(f"  [WARN] Indice {idx['nom']} non trouve")
                continue

            ds = dt_date.fromisoformat(idx["date_seance"])
            valeur = Decimal(str(idx["valeur"])) if idx["valeur"] is not None else None
            var = Decimal(str(idx["variation"])) if idx["variation"] is not None else None

            await conn.execute("""
                INSERT INTO cotations_indices (date_seance, indice_id, valeur, variation)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (date_seance, indice_id) DO UPDATE
                SET valeur = EXCLUDED.valeur, variation = EXCLUDED.variation
            """, ds, indice_id, valeur, var)
            indices_inseres += 1

        print(f"[DB] {indices_inseres} cotations indices inserees")

        # =============================================
        # ETAPE E : Inserer la seance du jour
        # =============================================
        date_seance_str = data.get("date", None)
        if date_seance_str:
            ds = dt_date.fromisoformat(date_seance_str)
            total_volume = sum(c["volume"] for c in cotations_data if c["volume"])
            await conn.execute("""
                INSERT INTO seances (date_seance, volume_total)
                VALUES ($1, $2)
                ON CONFLICT (date_seance) DO UPDATE SET volume_total = EXCLUDED.volume_total
            """, ds, total_volume)
            print(f"[DB] Seance du {date_seance_str} inseree (volume total: {total_volume})")

        # =============================================
        # ETAPE F : Log de collecte
        # =============================================
        await conn.execute("""
            INSERT INTO logs_collecte (source, statut, lignes_inserees)
            VALUES ($1, $2, $3)
        """, "brvm.org", "succes", cotations_inserees)
        print("[DB] Log de collecte enregistre")

        # =============================================
        # VERIFICATION : Compter les lignes inserees
        # =============================================
        print("")
        print("=" * 50)
        print("  VERIFICATION DES DONNEES EN BASE")
        print("=" * 50)

        nb_actions = await conn.fetchval("SELECT COUNT(*) FROM actions")
        nb_cotations = await conn.fetchval("SELECT COUNT(*) FROM cotations")
        nb_indices = await conn.fetchval("SELECT COUNT(*) FROM indices")
        nb_cot_indices = await conn.fetchval("SELECT COUNT(*) FROM cotations_indices")
        nb_seances = await conn.fetchval("SELECT COUNT(*) FROM seances")
        nb_logs = await conn.fetchval("SELECT COUNT(*) FROM logs_collecte")

        print(f"  actions           : {nb_actions} lignes")
        print(f"  cotations         : {nb_cotations} lignes")
        print(f"  indices           : {nb_indices} lignes")
        print(f"  cotations_indices : {nb_cot_indices} lignes")
        print(f"  seances           : {nb_seances} lignes")
        print(f"  logs_collecte     : {nb_logs} lignes")

        # Afficher un echantillon des cotations
        print("")
        print("  Echantillon des 5 premieres cotations en base :")
        rows = await conn.fetch("""
            SELECT a.ticker, c.prix, c.variation, c.volume, c.date_seance
            FROM cotations c
            JOIN actions a ON c.action_id = a.id
            ORDER BY a.ticker
            LIMIT 5
        """)
        for r in rows:
            var = r['variation'] if r['variation'] is not None else 0
            print(f"    {r['ticker']:8s} | {r['prix']:>8} FCFA | {var:>+.2f}% | vol: {r['volume']}")

        # Afficher les indices
        print("")
        print("  Indices en base :")
        idx_rows = await conn.fetch("""
            SELECT i.nom, ci.valeur, ci.variation, ci.date_seance
            FROM cotations_indices ci
            JOIN indices i ON ci.indice_id = i.id
            ORDER BY i.nom
        """)
        for r in idx_rows:
            print(f"    {r['nom']:20s} | {r['valeur']:>10.2f} | {r['variation']:>+.2f}%")

        print("")
        print("=" * 50)
        print("  INSERTION TERMINEE AVEC SUCCES")
        print("=" * 50)

    finally:
        await conn.close()
        print("[DB] Connexion fermee")


async def get_action_id_by_ticker_or_name(conn, ticker, nom):
    if ticker:
        row = await conn.fetchrow("SELECT id FROM actions WHERE ticker = $1", ticker)
        if row: return row['id']
    if nom:
        row = await conn.fetchrow("SELECT id FROM actions WHERE nom ILIKE $1", f"%{nom}%")
        if row: return row['id']
        # Try to match BOA
        if "BOA" in nom:
            nom_boa = nom.replace("BOA", "BANK OF AFRICA").strip()
            row = await conn.fetchrow("SELECT id FROM actions WHERE nom ILIKE $1", f"%{nom_boa}%")
            if row: return row['id']
    return None

async def insert_richbourse_data():
    """Insere les donnees scrappees depuis Richbourse dans TimescaleDB."""
    try:
        with open("richbourse_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("[WARN] richbourse_data.json introuvable.")
        return

    conn = await asyncpg.connect(**DB_CONFIG)
    print("[DB] Connexion a TimescaleDB etablie pour Richbourse")

    try:
        # 1. Notations
        notations_inserees = 0
        for n in data.get("notations", []):
            action_id = await get_action_id_by_ticker_or_name(conn, n.get("ticker"), None)
            if not action_id: continue

            await conn.execute("""
                INSERT INTO notations (action_id, agence, date_notation, note_court_terme, note_long_terme)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (action_id, agence, date_notation) DO UPDATE
                SET note_court_terme = EXCLUDED.note_court_terme, note_long_terme = EXCLUDED.note_long_terme
            """, action_id, n.get("agence"), n.get("date_notation"), n.get("note_court_terme"), n.get("note_long_terme"))
            notations_inserees += 1

        # 2. Dividendes
        dividendes_inseres = 0
        for d in data.get("dividendes", []):
            action_id = await get_action_id_by_ticker_or_name(conn, None, d.get("societe"))
            if not action_id: continue

            date_ex_div = dt_date.fromisoformat(d["date_ex_dividende"]) if d.get("date_ex_dividende") else None
            date_paiement = dt_date.fromisoformat(d["date_paiement"]) if d.get("date_paiement") else None
            montant = Decimal(str(d["dividende_fcfa"])) if d.get("dividende_fcfa") else Decimal('0')
            rendement = Decimal(str(d["rendement_pct"])) if d.get("rendement_pct") else None

            # On skip si montant net et date_paiement nulls ou conflict
            if not montant or not date_paiement:
                continue

            await conn.execute("""
                INSERT INTO dividendes (action_id, date_ex_dividende, date_paiement, montant_net, rendement_calcul)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (action_id, date_paiement, montant_net) DO UPDATE
                SET date_ex_dividende = EXCLUDED.date_ex_dividende, rendement_calcul = EXCLUDED.rendement_calcul
            """, action_id, date_ex_div, date_paiement, montant, rendement)
            dividendes_inseres += 1

        # 3. Actualites
        news_inserees = 0
        from datetime import datetime
        now = datetime.now()
        
        # Pre-charger le mapping nom/ticker -> action_id pour le linking
        actions_rows = await conn.fetch("SELECT id, ticker, nom FROM actions")
        # Build a list of (keyword, action_id) for fuzzy matching
        # keywords: ticker + first word of nom + mots significatifs
        action_keywords = []
        for a in actions_rows:
            action_keywords.append((a['ticker'].upper(), a['id']))
            # Also use each significant word from nom
            for word in a['nom'].split():
                if len(word) >= 4:  # skip tiny words like CI, DU, etc.
                    action_keywords.append((word.upper(), a['id']))
        
        def find_action_id(titre: str) -> int | None:
            titre_up = titre.upper()
            # Check ticker first (most precise)
            for kw, aid in action_keywords:
                if len(kw) >= 4 and kw in titre_up:
                    return aid
            return None

        for actu in data.get("actualites", []):
            try:
                date_pub_raw = actu.get("date_publication_raw")
                parsed_date = now
                if date_pub_raw:
                    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
                        try:
                            clean_d = date_pub_raw.split(" ")[0] 
                            parsed_date = datetime.strptime(clean_d, fmt)
                            break
                        except ValueError:
                            pass
                
                titre = actu.get("titre", "")
                action_id = find_action_id(titre)
                            
                await conn.execute("""
                    INSERT INTO news (action_id, date_publication, titre, url, provenance)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (url) DO UPDATE
                    SET action_id = COALESCE(EXCLUDED.action_id, news.action_id)
                """, action_id, parsed_date, titre, actu.get("url"), "Richbourse")
                news_inserees += 1
            except Exception:
                pass

        # 4. Logs
        await conn.execute("""
            INSERT INTO logs_collecte (source, statut, lignes_inserees)
            VALUES ($1, $2, $3)
        """, "richbourse.com", "succes", notations_inserees + dividendes_inseres + news_inserees)

        print(f"[DB] Richbourse : {notations_inserees} notations, {dividendes_inseres} dividendes, et {news_inserees} news.")

    finally:
        await conn.close()
        print("[DB] Connexion Richbourse fermee")


async def insert_sikafinance_data():
    """Insere les donnees scrappees depuis Sikafinance dans TimescaleDB."""
    try:
        with open("sikafinance_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("[WARN] sikafinance_data.json introuvable.")
        return

    conn = await asyncpg.connect(**DB_CONFIG)
    print("[DB] Connexion a TimescaleDB etablie pour Sikafinance")

    try:
        # 1. Indices Sectoriels
        indices_inseres = 0
        for idx in data.get("indices_sectoriels", []):
            nom = idx["nom"]
            # S'assurer que l'indice existe
            await conn.execute("INSERT INTO indices (nom) VALUES ($1) ON CONFLICT (nom) DO NOTHING", nom)
            indice_id = await conn.fetchval("SELECT id FROM indices WHERE nom = $1", nom)
            
            ds = dt_date.fromisoformat(idx["date_seance"])
            valeur = Decimal(str(idx["valeur"])) if idx["valeur"] is not None else None
            var = Decimal(str(idx["variation"])) if idx["variation"] is not None else None

            await conn.execute("""
                INSERT INTO cotations_indices (date_seance, indice_id, valeur, variation)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (date_seance, indice_id) DO UPDATE
                SET valeur = EXCLUDED.valeur, variation = EXCLUDED.variation
            """, ds, indice_id, valeur, var)
            indices_inseres += 1

        # 2. Secteurs (cotations_secteurs)
        secteurs_inseres = 0
        for s in data.get("secteurs", []):
            nom = s["nom"]
            await conn.execute("INSERT INTO secteurs (nom) VALUES ($1) ON CONFLICT (nom) DO NOTHING", nom)
            secteur_id = await conn.fetchval("SELECT id FROM secteurs WHERE nom = $1", nom)
            
            ds = dt_date.fromisoformat(s["date_seance"])
            ouvert = Decimal(str(s["ouverture"])) if s["ouverture"] is not None else None
            haut = Decimal(str(s["plus_haut"])) if s["plus_haut"] is not None else None
            bas = Decimal(str(s["plus_bas"])) if s["plus_bas"] is not None else None
            dernier = Decimal(str(s["dernier"])) if s["dernier"] is not None else None
            vj = Decimal(str(s["variation_jour"])) if s["variation_jour"] is not None else None
            vy = Decimal(str(s["variation_ytd"])) if s["variation_ytd"] is not None else None
            vol = int(s["volume"]) if s["volume"] else 0

            await conn.execute("""
                INSERT INTO cotations_secteurs (date_seance, secteur_id, ouverture, plus_haut, plus_bas, dernier, variation_jour, variation_ytd, volume)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (date_seance, secteur_id) DO UPDATE
                SET ouverture = EXCLUDED.ouverture, plus_haut = EXCLUDED.plus_haut, plus_bas = EXCLUDED.plus_bas, dernier = EXCLUDED.dernier, variation_jour = EXCLUDED.variation_jour, variation_ytd = EXCLUDED.variation_ytd, volume = EXCLUDED.volume
            """, ds, secteur_id, ouvert, haut, bas, dernier, vj, vy, vol)
            secteurs_inseres += 1

        # 3. Logs
        await conn.execute("""
            INSERT INTO logs_collecte (source, statut, lignes_inserees)
            VALUES ($1, $2, $3)
        """, "sikafinance.com", "succes", indices_inseres + secteurs_inseres)

        print(f"[DB] Sikafinance : {indices_inseres} indices sectoriels, {secteurs_inseres} cotations de secteurs.")

    finally:
        await conn.close()
        print("[DB] Connexion Sikafinance fermee")

if __name__ == "__main__":
    asyncio.run(insert_brvm_data())
    asyncio.run(insert_richbourse_data())
    asyncio.run(insert_sikafinance_data())
