from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from typing import List
import crud
import schemas

router = APIRouter(prefix="/market", tags=["Market"])

@router.get("/summary", response_model=schemas.MarketSummary)
async def get_summary(db: AsyncSession = Depends(get_db)):
    """Retourne un resume de la derniere seance de la BRVM."""
    market_data = await crud.get_market_summary(db)
    if not market_data:
        # Valeurs par defaut si la base est vide
        from datetime import date
        return schemas.MarketSummary(date_maj=date.today(), indices=[], volume_global=0, top_hausses=[], top_baisses=[])

    latest_date, indices, volume_global = market_data
    
    # Pour le resume, on a besoin du top hausses/baisses
    screener_data = await crud.get_screener(db)
    
    # Trier par variation
    sorted_screener = sorted(screener_data, key=lambda x: x["variation"], reverse=True)
    top_hausses = sorted_screener[:5]
    top_baisses = sorted_screener[-5:]
    top_baisses.reverse()

    return schemas.MarketSummary(
        date_maj=latest_date,
        indices=indices,
        volume_global=volume_global,
        top_hausses=top_hausses,
        top_baisses=top_baisses
    )

@router.get("/news")
async def get_market_news(limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    """Retourne le flux des dernieres actualites du marche."""
    news = await crud.get_all_news(db, limit=limit, offset=offset)
    return news

@router.get("/sectors", response_model=List[schemas.SectorPerformance])
async def get_sector_performance(db: AsyncSession = Depends(get_db)):
    """Retourne la performance par secteur d'activite."""
    sectors = await crud.get_sector_performance(db)
    return sectors
