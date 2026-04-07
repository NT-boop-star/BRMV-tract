"""
history_scraper.py
==================
Scrape l'historique complet des cotations BRVM via l'API Sikafinance (GetHistos),
depuis le 01/01/2000 jusqu'à aujourd'hui.

Fonctionnalités :
  - Reprend automatiquement depuis la dernière date en base par action
  - Mode --from-scratch : force le rechargement depuis 2000-01-01
  - Chunks de 85 jours max (limite API Sikafinance)
  - Logs détaillés avec estimation de durée restante
  - Gestion des erreurs et retry avec backoff exponentiel

Usage :
  python history_scraper.py              # Reprend depuis la dernière date en DB
  python history_scraper.py --from-scratch  # Recharge tout depuis 2000
  python history_scraper.py --ticker BICI.ci  # Seulement une action
"""

import sys
import io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import asyncio
import json
import time
import urllib.request
import urllib.error
import asyncpg
from datetime import datetime, date, timedelta

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "user": "brvm_user",
    "password": "brvm_password",
    "database": "brvm_tracker",
}

START_DATE_DEFAULT = date(2000, 1, 1)   # Date historique la plus ancienne
CHUNK_DAYS = 85                          # Max jours par requête API (~90j)
SLEEP_BETWEEN_CHUNKS = 0.35             # Secondes entre requêtes (throttle)
SLEEP_BETWEEN_ACTIONS = 1.0            # Secondes entre deux actions
MAX_RETRIES = 3                          # Nombre de tentatives par chunk
RETRY_BACKOFF = [2, 5, 10]             # Délais en secondes entre tentatives


# ---------------------------------------------------------------------------
# Mapping ticker -> suffixe Sikafinance
# ---------------------------------------------------------------------------
def get_sika_suffix(ticker: str, nom: str) -> str:
    """Retourne le suffixe pays correct pour l'API Sikafinance."""
    nom_upper = nom.upper()
    if ticker in ["BOAB", "BICB", "LNBB"] or "BENIN" in nom_upper:
        return ".bj"
    if ticker in ["BOABF", "CBIBF", "ONTBF"] or "BURKINA" in nom_upper:
        return ".bf"
    if ticker in ["BOAM"] or "MALI" in nom_upper:
        return ".ml"
    if ticker in ["BOAN"] or "NIGER" in nom_upper:
        return ".ne"
    if ticker in ["BOAS", "SNTS", "TTLS"] or "SENEGAL" in nom_upper:
        return ".sn"
    if ticker in ["ETIT", "ORGT"] or "TOGO" in nom_upper:
        return ".tg"
    return ".ci"


# ---------------------------------------------------------------------------
# Fetch d'un chunk de données historiques avec retry
# ---------------------------------------------------------------------------
async def fetch_history_chunk(sika_ticker: str, date_deb: date, date_fin: date) -> list:
    """
    Appelle l'API GetHistos de Sikafinance pour la période [date_deb, date_fin].
    Retries automatiques avec backoff exponentiel.
    """
    url = "https://www.sikafinance.com/api/general/GetHistos"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"https://www.sikafinance.com/marches/chartbourse/{sika_ticker}",
    }

    payload = json.dumps({
        "ticker": sika_ticker,
        "datedeb": date_deb.strftime("%Y-%m-%d"),
        "datefin": date_fin.strftime("%Y-%m-%d"),
        "xperiod": "0"
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    loop = asyncio.get_running_loop()

    def do_request():
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)

    for attempt in range(MAX_RETRIES):
        try:
            data = await loop.run_in_executor(None, do_request)
            return data.get("lst", [])
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = RETRY_BACKOFF[min(attempt, len(RETRY_BACKOFF) - 1)]
                print(f"      [!] Rate limit (429) – attente {wait}s avant retry...")
                await asyncio.sleep(wait)
            else:
                print(f"      [!] HTTP {e.code} pour {sika_ticker} [{date_deb} → {date_fin}]")
                return []
        except Exception as e:
            wait = RETRY_BACKOFF[min(attempt, len(RETRY_BACKOFF) - 1)]
            if attempt < MAX_RETRIES - 1:
                print(f"      [!] Erreur chunk {date_deb}→{date_fin} (tentative {attempt + 1}/{MAX_RETRIES}): {e}")
                await asyncio.sleep(wait)
            else:
                print(f"      [!] Abandon chunk {date_deb}→{date_fin} après {MAX_RETRIES} tentatives: {e}")
                return []
    return []


# ---------------------------------------------------------------------------
# Conversion des lignes API → enregistrements DB
# ---------------------------------------------------------------------------
def parse_rows(rows: list, action_id: int) -> list[tuple]:
    """Convertit les lignes JSON de l'API en tuples prêts pour asyncpg."""
    records = []
    for row in rows:
        try:
            d_str = row.get("Date", "")
            if not d_str:
                continue
            dt_obj = datetime.strptime(d_str, "%d/%m/%Y").date()

            close = row.get("Close")
            open_ = row.get("Open")
            high = row.get("High")
            low = row.get("Low")
            volume = row.get("Volume")

            # Validation : prix de clôture obligatoire
            if close is None or close == 0:
                continue

            records.append((
                dt_obj,        # date_seance
                action_id,     # action_id
                close,         # prix (clôture)
                open_,         # open
                high,          # high
                low,           # low
                None,          # variation (recalculée ultérieurement si besoin)
                volume,        # volume
            ))
        except Exception:
            pass
    return records


# ---------------------------------------------------------------------------
# Upsert en base
# ---------------------------------------------------------------------------
async def upsert_records(conn, records: list[tuple]) -> int:
    """Insère ou met à jour les cotations en base. Retourne le nombre de lignes."""
    if not records:
        return 0
    await conn.executemany("""
        INSERT INTO cotations (date_seance, action_id, prix, open, high, low, variation, volume)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (date_seance, action_id) DO UPDATE
        SET prix      = EXCLUDED.prix,
            open      = EXCLUDED.open,
            high      = EXCLUDED.high,
            low       = EXCLUDED.low,
            volume    = EXCLUDED.volume
    """, records)
    return len(records)


# ---------------------------------------------------------------------------
# Script principal
# ---------------------------------------------------------------------------
async def run_historic_scrape(from_scratch: bool = False, only_ticker: str = None):
    """
    Scrape l'historique complet depuis 2000-01-01.

    Args:
        from_scratch: Si True, ignore les données existantes et repart de 2000.
        only_ticker: Si fourni (ex: 'BICI'), traite seulement cette action.
    """
    print("=" * 65)
    print("  BRVM – SCRAPE HISTORIQUE DES COTATIONS (2000 → Aujourd'hui)")
    print("=" * 65)
    if from_scratch:
        print("  [MODE] --from-scratch  → Rechargement complet depuis 2000-01-01")
    else:
        print("  [MODE] Reprise depuis la dernière date en base par action")
    if only_ticker:
        print(f"  [FILTRE] Seulement : {only_ticker}")
    print()

    conn = await asyncpg.connect(**DB_CONFIG)

    try:
        # Charger toutes les actions (ou juste une si filtre)
        if only_ticker:
            actions = await conn.fetch(
                "SELECT id, ticker, nom FROM actions WHERE ticker = $1", only_ticker
            )
            if not actions:
                print(f"  [ERREUR] Ticker '{only_ticker}' introuvable en base.")
                return
        else:
            actions = await conn.fetch("SELECT id, ticker, nom FROM actions ORDER BY ticker")

        total_actions = len(actions)
        print(f"  {total_actions} action(s) à traiter.\n")

        total_inserted = 0
        global_start = time.monotonic()

        for idx, act in enumerate(actions, 1):
            action_id = act["id"]
            ticker = act["ticker"]
            nom = act["nom"]
            sika_ticker = f"{ticker}{get_sika_suffix(ticker, nom)}"

            # ---------------------------------------------------------------
            # Déterminer la date de départ pour cette action
            # ---------------------------------------------------------------
            if from_scratch:
                start_date = START_DATE_DEFAULT
            else:
                last_date = await conn.fetchval(
                    "SELECT MAX(date_seance) FROM cotations WHERE action_id = $1", action_id
                )
                if last_date:
                    # Reprendre le lendemain de la dernière cotation connue
                    start_date = last_date + timedelta(days=1)
                    if start_date > date.today():
                        print(f"  [{idx}/{total_actions}] {ticker:8s} – Déjà à jour (dernière: {last_date})")
                        continue
                else:
                    # Aucune donnée → repart de 2000
                    start_date = START_DATE_DEFAULT

            end_date = date.today()
            total_days = (end_date - start_date).days
            nb_chunks = max(1, -(-total_days // CHUNK_DAYS))  # ceil division

            print(f"  [{idx}/{total_actions}] {ticker:8s} ({sika_ticker}) | {start_date} → {end_date} | ~{nb_chunks} chunks")

            action_inserted = 0
            current_date = start_date
            chunk_num = 0
            action_start = time.monotonic()

            while current_date <= end_date:
                chunk_end = min(current_date + timedelta(days=CHUNK_DAYS - 1), end_date)
                chunk_num += 1

                rows = await fetch_history_chunk(sika_ticker, current_date, chunk_end)
                records = parse_rows(rows, action_id)

                if records:
                    inserted = await upsert_records(conn, records)
                    action_inserted += inserted

                    # Progression inline
                    pct = min(100, int((chunk_num / nb_chunks) * 100))
                    bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
                    elapsed = time.monotonic() - action_start
                    sys.stdout.write(
                        f"\r      [{bar}] {pct:3d}% | chunk {chunk_num}/{nb_chunks}"
                        f" | +{len(records)} pts | total: {action_inserted}"
                    )
                    sys.stdout.flush()

                await asyncio.sleep(SLEEP_BETWEEN_CHUNKS)
                current_date = chunk_end + timedelta(days=1)

            elapsed_action = time.monotonic() - action_start
            print(f"\r      ✓ {action_inserted:6d} cotations insérées pour {ticker:8s}"
                  f"  ({elapsed_action:.1f}s)")

            total_inserted += action_inserted

            # Estimation du temps global restant
            if idx < total_actions:
                elapsed_global = time.monotonic() - global_start
                avg_per_action = elapsed_global / idx
                remaining = avg_per_action * (total_actions - idx)
                mins, secs = divmod(int(remaining), 60)
                print(f"      → Temps estimé restant : {mins}m {secs:02d}s")

            await asyncio.sleep(SLEEP_BETWEEN_ACTIONS)

    finally:
        await conn.close()

    elapsed_total = time.monotonic() - global_start
    mins, secs = divmod(int(elapsed_total), 60)
    print()
    print("=" * 65)
    print(f"  ✓ COLLECTE TERMINÉE en {mins}m {secs:02d}s")
    print(f"  ✓ Lignes totales insérées / mises à jour : {total_inserted:,}")
    print("=" * 65)


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Scrape l'historique complet des cotations BRVM depuis 2000."
    )
    parser.add_argument(
        "--from-scratch",
        action="store_true",
        help="Recharge tout depuis 2000-01-01 (ignore la dernière date en base)"
    )
    parser.add_argument(
        "--ticker",
        type=str,
        default=None,
        help="Traiter seulement ce ticker (ex: BICI ou ETIT)"
    )

    args = parser.parse_args()
    asyncio.run(run_historic_scrape(
        from_scratch=args.from_scratch,
        only_ticker=args.ticker,
    ))
