from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any
from database import get_db

router = APIRouter()

@router.get("/indicators")
async def get_macro_indicators(db: AsyncSession = Depends(get_db)):
    """
    Récupère les indicateurs macro-économiques par pays (Croissance, Inflation).
    """
    query = """
        SELECT p.nom as pays, p.code, i.annee, i.croissance_pib, i.inflation, i.taux_bancarisation, i.population
        FROM indicateurs_macro i
        JOIN pays p ON i.pays_id = p.id
        ORDER BY i.annee DESC, p.nom
    """
    result = await db.execute(text(query))
    data = []
    for row in result.fetchall():
        data.append({
            "pays": row.pays,
            "code": row.code,
            "annee": row.annee,
            "croissance_pib": float(row.croissance_pib) if row.croissance_pib else None,
            "inflation": float(row.inflation) if row.inflation else None,
            "taux_bancarisation": float(row.taux_bancarisation) if row.taux_bancarisation else None,
            "population": row.population
        })
    return {"value": data, "Count": len(data)}

import yfinance as yf
from cachetools import TTLCache
from datetime import datetime

# Cache de 10 minutes pour éviter le rate-limit de Yahoo Finance
cache = TTLCache(maxsize=1, ttl=600)

@router.get("/commodities")
async def get_commodities_prices():
    """
    Récupère le prix actuel des principales matières premières via Yahoo Finance (temps-réel ou léger différé).
    """
    if "live_commodities" in cache:
        return cache["live_commodities"]

    # Tickers: CC=F (Cacao), GC=F (Or), CT=F (Coton), BZ=F (Brent)
    tickers_map = {
        "Cacao": {"ticker": "CC=F", "symbole": "USD", "unite": "Tonne"},
        "Or": {"ticker": "GC=F", "symbole": "USD", "unite": "Once"},
        "Coton": {"ticker": "CT=F", "symbole": "USc", "unite": "Livre"},
        "Pétrole Brent": {"ticker": "BZ=F", "symbole": "USD", "unite": "Baril"}
    }
    
    data = []
    try:
        tickers = getattr(yf, 'Tickers')(" ".join([v["ticker"] for v in tickers_map.values()]))
        
        for name, config in tickers_map.items():
            ticker_obj = tickers.tickers[config["ticker"]]
            hist = ticker_obj.history(period="5d")
            
            price = None
            variation = 0.0
            
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                price = hist['Close'].iloc[-1]
                if prev_close > 0:
                    variation = ((price - prev_close) / prev_close) * 100.0
            elif len(hist) == 1:
                price = hist['Close'].iloc[0]
                
            if price is not None:
                data.append({
                    "nom": name,
                    "symbole": config["symbole"],
                    "unite": config["unite"],
                    "prix": round(float(price), 2),
                    "variation_jour": round(float(variation), 2),
                    "date_jour": datetime.now().strftime("%Y-%m-%d")
                })
            
        result = {"value": data, "Count": len(data)}
        cache["live_commodities"] = result
        return result
    except Exception as e:
        print(f"Erreur YFinance : {e}")
        # En cas d'erreur API, retourner un ensemble vide
        return {"value": [], "Count": 0}
