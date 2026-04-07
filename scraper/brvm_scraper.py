"""
BRVM Scraper - Collecte des donnees du site officiel brvm.org
Sources conformes au cahier des charges :
  1. brvm.org/fr/cours-actions/0  -> 47 cours + variation + volume  (Playwright)
  2. brvm.org/fr/indices          -> Indices BRVM                   (Playwright)
  3. brvm.org/fr/annonces         -> Annonces emetteurs             (httpx)
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
BASE_URL = "https://www.brvm.org/fr"

# -----------------------------------------------
# Utilitaires
# -----------------------------------------------
def clean_number(text: str) -> float | None:
    """
    Convertit les nombres BRVM (espaces = milliers, virgule = decimal) en float.
    Ex: '2 930' -> 2930.0, '0,34' -> 0.34, '-1,18' -> -1.18
    """
    if not text or text.strip() == "" or text.strip() == "-":
        return None
    cleaned = text.strip().replace("\xa0", "").replace(" ", "").replace(",", ".")
    cleaned = re.sub(r'[^0-9.\-]', '', cleaned)
    try:
        return float(cleaned)
    except ValueError:
        return None

def clean_int(text: str) -> int | None:
    """Convertit un nombre entier BRVM en int Python."""
    val = clean_number(text)
    return int(val) if val is not None else None


# -----------------------------------------------
# 1. Scraper des cotations (47 actions) via Playwright
# -----------------------------------------------
async def scrape_cotations(page) -> list[dict]:
    """
    Scrape brvm.org/fr/cours-actions/0 via Playwright (page rendue JS)
    Colonnes: ticker, nom, volume, cours_veille, cours_ouverture, cours_cloture, variation
    """
    url = f"{BASE_URL}/cours-actions/0"
    print(f"[BRVM] Scraping cotations : {url}")

    await page.goto(url, wait_until="networkidle")
    # Attendre que le tableau se charge
    try:
        await page.wait_for_selector("table tbody tr", timeout=15000)
    except Exception:
        print("[BRVM] Timeout: le tableau des cotations ne s'est pas charge")
        return []

    rows = await page.query_selector_all("table tbody tr")
    cotations = []
    today = date.today().isoformat()

    for row in rows:
        cells = await row.query_selector_all("td")
        if len(cells) < 7:
            continue

        ticker = (await cells[0].inner_text()).strip()
        nom = (await cells[1].inner_text()).strip()
        volume = clean_int(await cells[2].inner_text())
        cours_veille = clean_int(await cells[3].inner_text())
        cours_ouverture = clean_int(await cells[4].inner_text())
        cours_cloture = clean_int(await cells[5].inner_text())
        variation = clean_number(await cells[6].inner_text())

        cotations.append({
            "date_seance": today,
            "ticker": ticker,
            "nom": nom,
            "volume": volume,
            "cours_veille": cours_veille,
            "cours_ouverture": cours_ouverture,
            "cours_cloture": cours_cloture,
            "variation": variation,
        })

    print(f"[BRVM] {len(cotations)} cotations extraites avec succes")
    return cotations


# -----------------------------------------------
# 2. Scraper des indices via la page de resume
# -----------------------------------------------
async def scrape_indices(page) -> list[dict]:
    """
    Scrape brvm.org/fr/resume pour les indices (Composite, BRVM 30, Prestige)
    Les indices sont dans la sidebar/section de la page de resume.
    """
    url = f"{BASE_URL}/cours-actions/0"
    print(f"[BRVM] Extraction des indices depuis la sidebar")

    # On est deja sur la page des cotations, les indices sont en sidebar
    # Cherchons les blocs d'indices (BRVM-C, BRVM-30, BRVM-PRES)
    indices = []
    today = date.today().isoformat()

    # Les indices sont dans des blocs .field-content ou similaires dans la sidebar
    # D'apres le screenshot, on voit: BRVM-C 410,68 0,26% / BRVM-30 192,49 0,31% / BRVM-PRES 159,60 0,03%
    # Essayons de les extraire depuis le contenu de la page
    content = await page.content()

    # Pattern pour les indices dans la sidebar
    import re as re_module
    # Cherchons les patterns de type "BRVM-C" suivi de valeurs
    index_patterns = [
        ("BRVM Composite", "BRVM-C"),
        ("BRVM 30", "BRVM-30"),
        ("BRVM Prestige", "BRVM-PRES"),
    ]

    for display_name, code in index_patterns:
        # Chercher dans le HTML le code de l'indice suivi de nombres
        pattern = rf'{code}\s*</?\w[^>]*>?\s*(\d[\d\s,\.]*)\s*</?\w[^>]*>?\s*([\-\+]?\d[\d,\.]*)\s*%?'
        match = re_module.search(pattern, content)
        if match:
            valeur = clean_number(match.group(1))
            variation = clean_number(match.group(2))
            indices.append({
                "date_seance": today,
                "nom": display_name,
                "code": code,
                "valeur": valeur,
                "variation": variation,
            })

    # Si le regex n'a pas marche, essayons via les elements DOM
    if not indices:
        # Chercher les elements contenant les noms d'indices
        all_text = await page.inner_text("body")
        for display_name, code in index_patterns:
            idx = all_text.find(code)
            if idx >= 0:
                # Extraire les nombres autour
                surrounding = all_text[idx:idx+50]
                nums = re.findall(r'[\d\s]+[,.]?\d+', surrounding)
                if len(nums) >= 2:
                    indices.append({
                        "date_seance": today,
                        "nom": display_name,
                        "code": code,
                        "valeur": clean_number(nums[0]),
                        "variation": clean_number(nums[1]),
                    })

    print(f"[BRVM] {len(indices)} indices extraits avec succes")
    return indices


# -----------------------------------------------
# 3. Scraper des capitalisations
# -----------------------------------------------
async def scrape_capitalisations(page) -> dict:
    """
    Extrait la capitalisation boursiere totale depuis la page des cotations.
    """
    print("[BRVM] Extraction des capitalisations")
    today = date.today().isoformat()

    all_text = await page.inner_text("body")
    caps = {}

    # Chercher "Capitalisation Actions" et le nombre associe
    cap_match = re.search(r'Capitalisation\s*Actions\s*([\d\s]+)\s*FCFA', all_text)
    if cap_match:
        caps["capitalisation_actions"] = clean_number(cap_match.group(1))

    # Chercher "Valeur des transactions"
    val_match = re.search(r'Valeur\s*des\s*transactions\s*([\d\s]+)\s*FCFA', all_text)
    if val_match:
        caps["valeur_transactions"] = clean_number(val_match.group(1))

    print(f"[BRVM] Capitalisations extraites: {len(caps)} metriques")
    return {"date_seance": today, **caps}


# -----------------------------------------------
# Point d'entree principal
# -----------------------------------------------
async def run_brvm_scraper():
    """Execute tous les scrapers BRVM via Playwright."""
    print("=" * 60)
    print("  BRVM SCRAPER - Collecte des donnees officielles")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        cotations = await scrape_cotations(page)
        indices = await scrape_indices(page)
        caps = await scrape_capitalisations(page)

        await browser.close()

    # Resume
    print("")
    print("-" * 60)
    print("  RESUME DE LA COLLECTE BRVM")
    print("-" * 60)
    print(f"  Cotations : {len(cotations)} actions")
    print(f"  Indices   : {len(indices)} indices")
    print(f"  Caps      : {caps}")
    print("-" * 60)

    # Apercu des 5 premieres cotations
    if cotations:
        print("")
        print("  Apercu des 5 premieres cotations :")
        for c in cotations[:5]:
            var = c['variation'] if c['variation'] is not None else 0
            prix = c['cours_cloture'] if c['cours_cloture'] is not None else 0
            print(f"     {c['ticker']:8s} | {prix:>8} FCFA | {var:>+.2f}%")

    # Indices
    if indices:
        print("")
        print("  Indices du jour :")
        for i in indices:
            var = f"{i['variation']:+.2f}%" if i['variation'] is not None else "N/A"
            val = f"{i['valeur']:.2f}" if i['valeur'] is not None else "N/A"
            print(f"     {i['nom']:20s} ({i['code']:10s}) | {val:>10s} | {var}")

    # Sauvegarder en JSON
    output = {
        "date": date.today().isoformat(),
        "cotations": cotations,
        "indices": indices,
        "capitalisations": caps,
    }
    with open("brvm_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n  [OK] Donnees sauvegardees dans brvm_data.json")

    return output


# -----------------------------------------------
if __name__ == "__main__":
    asyncio.run(run_brvm_scraper())
