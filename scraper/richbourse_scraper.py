"""
Richbourse Scraper - Collecte des donnees complementaires via Playwright
Sources conformes au cahier des charges :
  1. richbourse.com/common/variation/index       -> Palmares + variations + capitalisation
  2. richbourse.com/common/dividende/index        -> Dividendes
  3. richbourse.com/common/actualite/index         -> Actualites / publications
  4. richbourse.com/common/notation-financiere/index -> Notations financieres

Le site bloque httpx (403) -> Playwright obligatoire.
"""
import sys
import io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import asyncio
import re
import json
from datetime import date, datetime
from playwright.async_api import async_playwright

# -----------------------------------------------
# Configuration
# -----------------------------------------------
BASE_URL = "https://www.richbourse.com"

# -----------------------------------------------
# Utilitaires
# -----------------------------------------------
def clean_number(text: str) -> float | None:
    if not text or text.strip() in ("", "-", "(inconnue)"):
        return None
    cleaned = text.strip().replace("\xa0", "").replace(" ", "").replace(",", ".").replace("%", "")
    cleaned = re.sub(r'[^0-9.\-]', '', cleaned)
    try:
        return float(cleaned)
    except ValueError:
        return None

def clean_int(text: str) -> int | None:
    val = clean_number(text)
    return int(val) if val is not None else None


# -----------------------------------------------
# 1. Palmares / Variations
# -----------------------------------------------
async def scrape_variations(page) -> list[dict]:
    """
    Scrape richbourse.com/common/variation/index
    10 colonnes: [fleche, Symbole, Action, Variation, Volume, Valeur(FCFA),
                  Cours actuel, Cours veille, Capitalisation, icone]
    La premiere ligne de donnees est un TOTAL a ignorer.
    """
    print("[RichBourse] Scraping palmares / variations...")
    await page.goto(f"{BASE_URL}/common/variation/index", wait_until="networkidle")

    tables = await page.query_selector_all("table")
    if not tables:
        print("  [WARN] Aucun tableau trouve")
        return []

    rows = await tables[0].query_selector_all("tr")
    variations = []
    today = date.today().isoformat()

    for i, row in enumerate(rows[1:]):  # skip header
        cells = await row.query_selector_all("td")
        if len(cells) < 9:
            continue

        ticker = (await cells[1].inner_text()).strip()
        nom = (await cells[2].inner_text()).strip()

        # Ignorer la ligne TOTAL
        if ticker == "" or nom == "TOTAL":
            continue

        variation = clean_number(await cells[3].inner_text())
        volume = clean_int(await cells[4].inner_text())
        valeur = clean_int(await cells[5].inner_text())
        cours_actuel = clean_int(await cells[6].inner_text())
        cours_veille = clean_int(await cells[7].inner_text())
        capitalisation = clean_int(await cells[8].inner_text())

        variations.append({
            "date_seance": today,
            "ticker": ticker,
            "nom": nom,
            "variation": variation,
            "volume": volume,
            "valeur_fcfa": valeur,
            "cours_actuel": cours_actuel,
            "cours_veille": cours_veille,
            "capitalisation": capitalisation,
        })

    print(f"[RichBourse] {len(variations)} lignes de variations extraites")
    return variations


# -----------------------------------------------
# 2. Dividendes
# -----------------------------------------------
async def scrape_dividendes(page) -> list[dict]:
    """
    Scrape richbourse.com/common/dividende/index
    7 colonnes: [#, Societe, Dividende, Rendement, Ex-dividende, Date paiement, icone]
    """
    print("[RichBourse] Scraping dividendes...")
    await page.goto(f"{BASE_URL}/common/dividende/index", wait_until="networkidle")

    tables = await page.query_selector_all("table")
    if not tables:
        print("  [WARN] Aucun tableau trouve")
        return []

    rows = await tables[0].query_selector_all("tr")
    dividendes = []

    for row in rows[1:]:  # skip header
        cells = await row.query_selector_all("td")
        if len(cells) < 6:
            continue

        societe = (await cells[1].inner_text()).strip()
        dividende = clean_number(await cells[2].inner_text())
        rendement = clean_number(await cells[3].inner_text())
        date_ex_div = (await cells[4].inner_text()).strip()
        date_paiement = (await cells[5].inner_text()).strip()

        if not societe:
            continue

        # Parser les dates
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
            try:
                date_ex_div = datetime.strptime(date_ex_div, fmt).strftime("%Y-%m-%d")
                break
            except ValueError:
                pass

        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
            try:
                date_paiement = datetime.strptime(date_paiement, fmt).strftime("%Y-%m-%d")
                break
            except ValueError:
                pass

        dividendes.append({
            "societe": societe,
            "dividende_fcfa": dividende,
            "rendement_pct": rendement,
            "date_ex_dividende": date_ex_div if date_ex_div != "(inconnue)" else None,
            "date_paiement": date_paiement if date_paiement != "(inconnue)" else None,
        })

    print(f"[RichBourse] {len(dividendes)} lignes de dividendes extraites")
    return dividendes


# -----------------------------------------------
# 3. Actualites
# -----------------------------------------------
async def scrape_actualites(page, max_pages: int = 5, start_page: int = 1) -> list[dict]:
    """
    Scrape richbourse.com/common/actualite/index
    Recupere la date, le titre, et le lien des actualites.
    """
    print(f"[RichBourse] Scraping actualites historiques (de la page {start_page} à {max_pages})...")
    actualites = []
    
    # URL de base des actualites
    url_base = f"{BASE_URL}/common/actualite/index"

    for page_num in range(start_page, max_pages + 1):
        try:
            url = f"{url_base}?page={page_num}" if page_num > 1 else url_base
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            
            # Wait a bit instead of strict selector
            await page.wait_for_timeout(3000)
            
            rows = await page.query_selector_all(".ligne_impaire, .ligne_paire")
            if not rows:
                print(f"  [WARN] Pas d'articles (pas de .ligne) sur la page {page_num}")
                break
                
            for row in rows:
                date_el = await row.query_selector("div:nth-child(1)")
                link_el = await row.query_selector("div:nth-child(2) a")
                
                if not date_el or not link_el:
                    continue
                    
                date_str = (await date_el.inner_text()).strip()
                titre = (await link_el.inner_text()).strip()
                href = await link_el.get_attribute("href")
                url_actu = f"{BASE_URL}{href}" if href and href.startswith("/") else (href or "")

                if not titre:
                    continue

                actualites.append({
                    "date_publication_raw": date_str,
                    "titre": titre,
                    "url": url_actu,
                })
                
            print(f"  ... Page {page_num} extraite ({len(rows)} articles)")
            import random
            await asyncio.sleep(random.uniform(1.5, 3.0)) # Pause anti-bot
                
        except Exception as e:
            print(f"  [WARN] Erreur pagination {page_num} : {e}")
            break

    print(f"[RichBourse] {len(actualites)} actualites historiques extraites")
    return actualites


# -----------------------------------------------
# 4. Notations financieres
# -----------------------------------------------
async def scrape_notations(page, tickers: list[str]) -> list[dict]:
    """
    Scrape richbourse.com/common/notation-financiere/index/[TICKER]
    """
    print(f"[RichBourse] Scraping notations ({len(tickers)} tickers)...")
    notations = []

    for ticker in tickers:
        try:
            await page.goto(f"{BASE_URL}/common/notation-financiere/index/{ticker}", wait_until="networkidle", timeout=10000)
        except Exception:
            continue

        tables = await page.query_selector_all("table")
        if not tables:
            continue

        rows = await tables[0].query_selector_all("tr")
        for row in rows[1:]:
            cells = await row.query_selector_all("td")
            if len(cells) < 4:
                continue

            agence = (await cells[0].inner_text()).strip()
            date_notation = (await cells[1].inner_text()).strip()
            note_ct = (await cells[2].inner_text()).strip()
            note_lt = (await cells[3].inner_text()).strip()

            if not agence:
                continue

            notations.append({
                "ticker": ticker,
                "agence": agence,
                "date_notation": date_notation,
                "note_court_terme": note_ct,
                "note_long_terme": note_lt,
            })

    print(f"[RichBourse] {len(notations)} notations extraites")
    return notations


# -----------------------------------------------
# Point d'entree principal
# -----------------------------------------------
async def run_richbourse_scraper():
    """Execute tous les scrapers Richbourse."""
    print("")
    print("=" * 60)
    print("  RICHBOURSE SCRAPER - Donnees complementaires")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Variations
        variations = await scrape_variations(page)

        # 2. Dividendes
        dividendes = await scrape_dividendes(page)

        # 3. Actualites (5 pages pour la collecte quotidienne)
        actualites = await scrape_actualites(page, max_pages=5)

        # 4. Notations (TOUS les tickers)
        tickers = [v["ticker"] for v in variations]
        notations = await scrape_notations(page, tickers) if tickers else []

        await browser.close()

    # Resume
    print("")
    print("-" * 60)
    print("  RESUME DE LA COLLECTE RICHBOURSE")
    print("-" * 60)
    print(f"  Variations  : {len(variations)} lignes")
    print(f"  Dividendes  : {len(dividendes)} lignes")
    print(f"  Actualites  : {len(actualites)} articles")
    print(f"  Notations   : {len(notations)} notations")
    print("-" * 60)

    # Apercu
    if variations:
        print("")
        print("  Top 5 hausses du jour :")
        for v in variations[:5]:
            var = v['variation'] if v['variation'] is not None else 0
            prix = v['cours_actuel'] if v['cours_actuel'] is not None else 0
            cap = v['capitalisation'] if v['capitalisation'] is not None else 0
            print(f"     {v['ticker']:8s} | {prix:>8} FCFA | {var:>+.2f}% | Cap: {cap:>15}")

    if dividendes:
        print("")
        print("  Dividendes (5 premiers) :")
        for d in dividendes[:5]:
            div = d['dividende_fcfa'] if d['dividende_fcfa'] is not None else 0
            rend = d['rendement_pct'] if d['rendement_pct'] is not None else 0
            print(f"     {d['societe']:25s} | {div:>8} FCFA | Rend: {rend:.2f}%")

    # Sauvegarder en JSON
    output = {
        "date": date.today().isoformat(),
        "variations": variations,
        "dividendes": dividendes,
        "actualites": actualites,
        "notations": notations,
    }
    with open("richbourse_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n  [OK] Donnees sauvegardees dans richbourse_data.json")

    return output


# -----------------------------------------------
if __name__ == "__main__":
    asyncio.run(run_richbourse_scraper())
