"""
Sikafinance Scraper - Collecte des donnees complementaires via Playwright
Sources conformes au cahier des charges :
  1. sikafinance.com/marches/aaz        -> Cotations A-Z + indices sectoriels
  2. sikafinance.com/marches/palmares    -> Palmares hausse/baisse
  3. sikafinance.com/marches/dividendes  -> Dividendes a venir
  4. sikafinance.com/marches/secteurs    -> Donnees sectorielles

Toutes les pages sont rendues par JavaScript -> Playwright obligatoire.
"""
import sys
import io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import asyncio
import re
import json
from datetime import date
from playwright.async_api import async_playwright

# -----------------------------------------------
# Configuration
# -----------------------------------------------
BASE_URL = "https://www.sikafinance.com"

# -----------------------------------------------
# Utilitaires
# -----------------------------------------------
def clean_number(text: str) -> float | None:
    if not text or text.strip() in ("", "-", "N/A"):
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
# 1. Cotations A-Z + Indices sectoriels
# -----------------------------------------------
async def scrape_aaz(page) -> dict:
    """
    Scrape sikafinance.com/marches/aaz
    - Indices sectoriels (haut de page)
    - Actions cotees (bas de page) : Nom, Ouverture, +Haut, +Bas, Volume(titres), Volume(XOF), Dernier, Variation
    """
    print("[Sikafinance] Scraping cotations A-Z...")
    try:
        await page.goto(f"{BASE_URL}/marches/aaz", wait_until="networkidle", timeout=45000)
    except Exception:
        try:
            await page.goto(f"{BASE_URL}/marches/aaz", wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(5000)
        except Exception as e:
            print(f"  [WARN] Impossible de charger la page A-Z : {e}")
            return {"indices_sectoriels": [], "cotations": []}

    try:
        await page.wait_for_selector("table", timeout=15000)
    except Exception:
        print("  [WARN] Timeout: tableau non charge")
        return {"indices_sectoriels": [], "cotations": []}

    tables = await page.query_selector_all("table")
    today = date.today().isoformat()

    # --- Indices sectoriels (1er tableau) ---
    # Colonnes Sikafinance indices: Nom | Ouverture | +Haut | +Bas | Dernier | Variation
    # La variation est dans la DERNIERE colonne (index -1)
    indices_sectoriels = []
    if len(tables) >= 1:
        rows = await tables[0].query_selector_all("tr")
        for row in rows:
            cells = await row.query_selector_all("td")
            if len(cells) < 5:
                continue
            nom = (await cells[0].inner_text()).strip()
            if not nom or nom == "Nom":
                continue
            # Dernier = avant-derniere colonne, Variation = derniere colonne
            dernier = clean_number(await cells[-2].inner_text())
            variation = clean_number(await cells[-1].inner_text())
            indices_sectoriels.append({
                "date_seance": today,
                "nom": nom,
                "valeur": dernier,
                "variation": variation,
            })

    print(f"[Sikafinance] {len(indices_sectoriels)} indices sectoriels extraits")

    # --- Actions cotees (2eme tableau) ---
    cotations = []
    if len(tables) >= 2:
        rows = await tables[1].query_selector_all("tr")
        for row in rows:
            cells = await row.query_selector_all("td")
            if len(cells) < 7:
                continue
            nom = (await cells[0].inner_text()).strip()
            if not nom or nom == "Nom":
                continue
            ouverture = clean_int(await cells[1].inner_text())
            plus_haut = clean_int(await cells[2].inner_text())
            plus_bas = clean_int(await cells[3].inner_text())
            volume_titres = clean_int(await cells[4].inner_text())
            volume_xof = clean_int(await cells[5].inner_text())
            dernier = clean_int(await cells[6].inner_text())
            variation = clean_number(await cells[7].inner_text()) if len(cells) > 7 else None

            cotations.append({
                "date_seance": today,
                "nom": nom,
                "ouverture": ouverture,
                "plus_haut": plus_haut,
                "plus_bas": plus_bas,
                "volume_titres": volume_titres,
                "volume_xof": volume_xof,
                "dernier": dernier,
                "variation": variation,
            })

    print(f"[Sikafinance] {len(cotations)} cotations A-Z extraites")
    return {"indices_sectoriels": indices_sectoriels, "cotations": cotations}


# -----------------------------------------------
# 2. Palmares
# -----------------------------------------------
async def scrape_palmares(page) -> dict:
    """
    Scrape sikafinance.com/marches/palmares
    Hausse, Baisse, Volumes
    """
    print("[Sikafinance] Scraping palmares...")
    try:
        await page.goto(f"{BASE_URL}/marches/palmares", wait_until="networkidle", timeout=45000)
    except Exception:
        try:
            await page.goto(f"{BASE_URL}/marches/palmares", wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(5000)
        except Exception as e:
            print(f"  [WARN] Impossible de charger la page palmares : {e}")
            return {"hausses": [], "baisses": [], "volumes": []}

    try:
        await page.wait_for_selector("table", timeout=15000)
    except Exception:
        print("  [WARN] Timeout: palmares non charge")
        return {"hausses": [], "baisses": [], "volumes": []}

    tables = await page.query_selector_all("table")
    today = date.today().isoformat()

    async def parse_table(table) -> list[dict]:
        """Parse palmares table. Colonnes: Nom | Haut | Bas | Dernier | Volume | Variation jour."""
        items = []
        rows = await table.query_selector_all("tr")
        for row in rows:
            cells = await row.query_selector_all("td")
            if len(cells) < 5:
                continue
            nom = (await cells[0].inner_text()).strip()
            if not nom or nom == "Nom":
                continue
            haut = clean_int(await cells[1].inner_text())
            bas = clean_int(await cells[2].inner_text())
            dernier = clean_int(await cells[3].inner_text())
            volume = clean_int(await cells[4].inner_text())
            variation = clean_number(await cells[5].inner_text()) if len(cells) > 5 else None
            items.append({
                "date_seance": today,
                "nom": nom,
                "plus_haut": haut,
                "plus_bas": bas,
                "dernier": dernier,
                "volume": volume,
                "variation": variation,
            })
        return items

    # Page palmares = 1 seul tableau avec toutes les donnees (hausse + baisse)
    all_items = await parse_table(tables[0]) if len(tables) > 0 else []
    # Separer hausses et baisses selon le signe de la variation
    hausses = [i for i in all_items if (i['variation'] or 0) > 0]
    baisses = [i for i in all_items if (i['variation'] or 0) < 0]
    neutres = [i for i in all_items if (i['variation'] or 0) == 0]

    print(f"[Sikafinance] Palmares: {len(hausses)} hausses, {len(baisses)} baisses, {len(neutres)} neutres")
    return {"hausses": hausses, "baisses": baisses, "neutres": neutres}


# -----------------------------------------------
# 3. Dividendes
# -----------------------------------------------
async def scrape_dividendes(page) -> list[dict]:
    """
    Scrape sikafinance.com/marches/dividendes
    Colonnes: Date detachement, Nom, Montant, Rendement
    """
    print("[Sikafinance] Scraping dividendes...")
    try:
        await page.goto(f"{BASE_URL}/marches/dividendes", wait_until="networkidle", timeout=45000)
    except Exception:
        try:
            await page.goto(f"{BASE_URL}/marches/dividendes", wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(5000)
        except Exception as e:
            print(f"  [WARN] Impossible de charger la page dividendes : {e}")
            return []

    try:
        await page.wait_for_selector("table", timeout=15000)
    except Exception:
        print("  [WARN] Timeout: dividendes non charge")
        return []

    tables = await page.query_selector_all("table")
    if not tables:
        return []

    rows = await tables[0].query_selector_all("tr")
    dividendes = []

    for row in rows:
        cells = await row.query_selector_all("td")
        if len(cells) < 4:
            continue
        date_det = (await cells[0].inner_text()).strip()
        nom = (await cells[1].inner_text()).strip()
        montant = clean_number(await cells[2].inner_text())
        rendement = clean_number(await cells[3].inner_text())

        if not nom or nom == "Nom":
            continue

        dividendes.append({
            "date_detachement": date_det if date_det else None,
            "nom": nom,
            "montant_fcfa": montant,
            "rendement_pct": rendement,
        })

    print(f"[Sikafinance] {len(dividendes)} dividendes extraits")
    return dividendes


# -----------------------------------------------
# 4. Secteurs
# -----------------------------------------------
async def scrape_secteurs(page) -> list[dict]:
    """
    Scrape sikafinance.com/marches/secteurs
    Recupere le tableau par defaut (tous secteurs affiches).
    """
    print("[Sikafinance] Scraping secteurs...")
    try:
        await page.goto(f"{BASE_URL}/marches/secteurs", wait_until="networkidle", timeout=45000)
    except Exception:
        # Fallback: tenter avec un wait_until moins strict
        try:
            await page.goto(f"{BASE_URL}/marches/secteurs", wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(5000)
        except Exception as e:
            print(f"  [WARN] Impossible de charger la page secteurs : {e}")
            return []

    try:
        await page.wait_for_selector("table", timeout=15000)
    except Exception:
        print("  [WARN] Timeout: secteurs non charge")
        return []

    tables = await page.query_selector_all("table")
    if not tables:
        return []

    rows = await tables[0].query_selector_all("tr")
    today = date.today().isoformat()
    secteurs = []

    for row in rows:
        cells = await row.query_selector_all("td")
        if len(cells) < 6:
            continue
        nom = (await cells[0].inner_text()).strip()
        if not nom or nom == "Nom":
            continue
        ouverture = clean_number(await cells[1].inner_text())
        plus_haut = clean_number(await cells[2].inner_text())
        plus_bas = clean_number(await cells[3].inner_text())
        volume = clean_int(await cells[4].inner_text())
        dernier = clean_number(await cells[5].inner_text())
        var_jour = clean_number(await cells[6].inner_text()) if len(cells) > 6 else None
        var_ytd = clean_number(await cells[7].inner_text()) if len(cells) > 7 else None

        secteurs.append({
            "date_seance": today,
            "nom": nom,
            "ouverture": ouverture,
            "plus_haut": plus_haut,
            "plus_bas": plus_bas,
            "volume": volume,
            "dernier": dernier,
            "variation_jour": var_jour,
            "variation_ytd": var_ytd,
        })

    print(f"[Sikafinance] {len(secteurs)} secteurs extraits")
    return secteurs


# -----------------------------------------------
# Point d'entree principal
# -----------------------------------------------
async def run_sikafinance_scraper():
    """Execute tous les scrapers Sikafinance."""
    print("")
    print("=" * 60)
    print("  SIKAFINANCE SCRAPER - Donnees complementaires")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # 1. Cotations A-Z + indices sectoriels
        aaz = await scrape_aaz(page)

        # 2. Palmares
        palmares = await scrape_palmares(page)

        # 3. Dividendes
        dividendes = await scrape_dividendes(page)

        # 4. Secteurs
        secteurs = await scrape_secteurs(page)

        await browser.close()

    # Resume
    print("")
    print("-" * 60)
    print("  RESUME DE LA COLLECTE SIKAFINANCE")
    print("-" * 60)
    print(f"  Indices sectoriels : {len(aaz['indices_sectoriels'])} indices")
    print(f"  Cotations A-Z      : {len(aaz['cotations'])} actions")
    print(f"  Palmares hausses   : {len(palmares['hausses'])} / baisses : {len(palmares['baisses'])}")
    print(f"  Dividendes         : {len(dividendes)} lignes")
    print(f"  Secteurs           : {len(secteurs)} secteurs")
    print("-" * 60)

    # Apercu
    if aaz['cotations']:
        print("")
        print("  5 premieres cotations A-Z :")
        for c in aaz['cotations'][:5]:
            prix = c['dernier'] if c['dernier'] is not None else 0
            var = c['variation'] if c['variation'] is not None else 0
            print(f"     {c['nom']:30s} | {prix:>8} FCFA | {var:>+.2f}%")

    if aaz['indices_sectoriels']:
        print("")
        print("  Indices sectoriels :")
        for i in aaz['indices_sectoriels'][:8]:
            val = i['valeur'] if i['valeur'] is not None else 0
            var = i['variation'] if i['variation'] is not None else 0
            print(f"     {i['nom']:30s} | {val:>12.2f} | {var:>+.2f}%")

    # Sauvegarder
    output = {
        "date": date.today().isoformat(),
        "indices_sectoriels": aaz["indices_sectoriels"],
        "cotations_aaz": aaz["cotations"],
        "palmares": palmares,
        "dividendes": dividendes,
        "secteurs": secteurs,
    }
    with open("sikafinance_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n  [OK] Donnees sauvegardees dans sikafinance_data.json")

    return output


# -----------------------------------------------
if __name__ == "__main__":
    asyncio.run(run_sikafinance_scraper())
