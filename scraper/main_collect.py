"""
Service de Collecte Automatique - BRVM Tracker
================================================
Planifie le scraping et l'insertion en base de donnees
de facon automatique, chaque jour ouvre a la cloture du marche BRVM.

Marche BRVM : ouverture 09h00 - cloture 15h30 (heure Abidjan, GMT+0)
Le scraping est programme a 16h00 GMT pour s'assurer que toutes
les donnees de cloture sont publiees.

Usage :
  python main_collect.py              -> lance le scheduler (tourne en continu)
  python main_collect.py --now        -> lance une collecte immediate puis quitte
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import asyncio
import argparse
from datetime import datetime, date
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# Import des scrapers et de l'insertion
from brvm_scraper import run_brvm_scraper
from richbourse_scraper import run_richbourse_scraper
from insert_db import insert_brvm_data


# -----------------------------------------------
# Fonction de collecte complete (scrape + insert)
# -----------------------------------------------
def run_collecte():
    """Execute le pipeline complet : scraping BRVM + insertion en base."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("")
    print("=" * 60)
    print(f"  COLLECTE AUTOMATIQUE - {now}")
    print("=" * 60)

    try:
        # Etape 1/3 : Scraping BRVM
        print("[1/3] Lancement du scraping BRVM...")
        result_brvm = asyncio.run(run_brvm_scraper())

        nb_cotations = len(result_brvm.get("cotations", []))
        nb_indices = len(result_brvm.get("indices", []))

        if nb_cotations == 0:
            print("[WARN] Aucune cotation BRVM scrappee. Le marche est peut-etre ferme.")
        else:
            # Etape 2/3 : Insertion BRVM en base
            print(f"[2/3] Insertion de {nb_cotations} cotations et {nb_indices} indices BRVM...")
            asyncio.run(insert_brvm_data())
            print(f"     BRVM : {nb_cotations} cotations / {nb_indices} indices inseres")

        # Etape 3/4 : Scraping Richbourse
        print("[3/4] Lancement du scraping Richbourse...")
        result_rb = asyncio.run(run_richbourse_scraper())

        nb_variations = len(result_rb.get("variations", []))
        nb_dividendes = len(result_rb.get("dividendes", []))
        nb_actualites = len(result_rb.get("actualites", []))
        nb_notations = len(result_rb.get("notations", []))
        print(f"     Richbourse : {nb_variations} variations / {nb_dividendes} dividendes / {nb_actualites} actualites / {nb_notations} notations")
        
        from insert_db import insert_richbourse_data
        asyncio.run(insert_richbourse_data())

        # Etape 4/4 : Scraping Sikafinance
        print("[4/4] Lancement du scraping Sikafinance...")
        from sikafinance_scraper import run_sikafinance_scraper
        result_sika = asyncio.run(run_sikafinance_scraper())

        nb_cotations_sika = len(result_sika.get("cotations_aaz", []))
        nb_indices_sika = len(result_sika.get("indices_sectoriels", []))
        nb_palmares = len(result_sika.get("palmares", {}).get("hausses", [])) + len(result_sika.get("palmares", {}).get("baisses", []))
        nb_secteurs = len(result_sika.get("secteurs", []))
        print(f"     Sikafinance : {nb_cotations_sika} cotations / {nb_indices_sika} indices / {nb_palmares} palmares / {nb_secteurs} secteurs")

        from insert_db import insert_sikafinance_data
        asyncio.run(insert_sikafinance_data())

        # Etape 5/5 : Scraping Indicateurs Macro-économiques (World Bank)
        print("[5/5] Mise à jour des indicateurs macro-économiques...")
        import macro_scraper
        macro_scraper.fetch_world_bank_data()

        print("")
        print(f"[OK] Collecte terminee avec succes a {now}")

    except Exception as e:
        print(f"[ERREUR] Collecte echouee : {e}")
        import traceback
        traceback.print_exc()


# -----------------------------------------------
# Scheduler (APScheduler)
# -----------------------------------------------
def start_scheduler():
    """
    Lance le scheduler APScheduler.
    Planifie la collecte :
      - Du lundi au vendredi (jours ouvres)
      - A 16h00 GMT (apres la cloture a 15h30)
    """
    scheduler = BlockingScheduler()

    # Planification : lundi-vendredi a 16h00 UTC
    trigger = CronTrigger(
        day_of_week="mon-fri",
        hour=16,
        minute=0,
        timezone="UTC"
    )

    scheduler.add_job(
        run_collecte,
        trigger=trigger,
        id="brvm_daily_collect",
        name="Collecte quotidienne BRVM",
        replace_existing=True,
    )

    print("=" * 60)
    print("  SERVICE DE COLLECTE BRVM TRACKER")
    print("=" * 60)
    print(f"  Demarrage : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Planification : lundi-vendredi a 16h00 UTC")
    print(f"  (apres cloture du marche BRVM a 15h30 GMT)")
    print("")
    print("  Sources configurees :")
    print("    [x] brvm.org    -> cotations, indices, capitalisations")
    print("    [x] richbourse  -> variations, dividendes, actualites, notations")
    print("    [x] sikafinance -> cotations A-Z, palmares, secteurs")
    print("")
    print("  Le service tourne en continu. Ctrl+C pour arreter.")
    print("=" * 60)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n[STOP] Service de collecte arrete proprement.")
        scheduler.shutdown()


# -----------------------------------------------
# Point d'entree
# -----------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Service de collecte BRVM Tracker")
    parser.add_argument(
        "--now",
        action="store_true",
        help="Lance une collecte immediate puis quitte"
    )
    args = parser.parse_args()

    if args.now:
        # Mode immediat : scrape + insert puis quitte
        print("[MODE] Collecte immediate demandee")
        run_collecte()
    else:
        # Mode scheduler : tourne en continu
        start_scheduler()
