from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date, timedelta
from database import get_db
import crud
import schemas

router = APIRouter(prefix="/actions", tags=["Actions"])


@router.get("/", response_model=List[schemas.ActionWithSecteur])
async def list_actions(db: AsyncSession = Depends(get_db)):
    """Retourne la liste de toutes les actions actives."""
    return await crud.get_all_actions(db)


@router.get("/screener", response_model=List[schemas.ScreenerRow])
async def get_screener(db: AsyncSession = Depends(get_db)):
    """Retourne les données du screener (dernières cotations de toutes les actions)."""
    return await crud.get_screener(db)


@router.get("/{ticker}", response_model=schemas.ActionDetailResponse)
async def get_action_details(ticker: str, db: AsyncSession = Depends(get_db)):
    """Retourne les détails d'une action : dividendes, notation, actualités, dernière cotation."""
    action = await crud.get_action_by_ticker(db, ticker)
    if not action:
        raise HTTPException(status_code=404, detail="Action introuvable")

    derniere_cot = await crud.get_derniere_cotation(db, action.id)
    dividendes = await crud.get_dividendes_action(db, action.id)
    notations = await crud.get_notations_action(db, action.id)
    news = await crud.get_news_action(db, action.id, limit=500)
    rapports_annuels = await crud.get_rapports_annuels_action(db, action.id)

    return schemas.ActionDetailResponse(
        action=action,
        derniere_cotation=derniere_cot,
        dividendes=dividendes,
        notations=notations,
        news=news,
        rapports_annuels=rapports_annuels
    )


@router.get("/{ticker}/chart", response_model=List[schemas.ChartData])
async def get_action_chart(
    ticker: str,
    from_date: Optional[date] = Query(
        None,
        description="Date de début ISO (YYYY-MM-DD). Si absent, remonte jusqu'au 2000-01-01.",
    ),
    to_date: Optional[date] = Query(
        None,
        description="Date de fin ISO (YYYY-MM-DD). Si absent, utilise aujourd'hui.",
    ),
    days: Optional[int] = Query(
        None,
        description="[Compat] Nombre de jours depuis aujourd'hui. Ignoré si from_date est fourni.",
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Retourne l'historique OHLCV d'une action pour les graphiques.

    - Par défaut (aucun paramètre) : tout l'historique depuis 2000-01-01.
    - `from_date` / `to_date` : plage de dates précise.
    - `days` : raccourci – N derniers jours (rétrocompat).

    Exemples :
      /actions/SGBC/chart                          → tout l'historique (2000→aujourd'hui)
      /actions/SGBC/chart?from_date=2010-01-01     → depuis 2010
      /actions/SGBC/chart?days=365                 → 1 an glissant
    """
    action = await crud.get_action_by_ticker(db, ticker)
    if not action:
        raise HTTPException(status_code=404, detail="Action introuvable")

    # Résoudre from_date si seul `days` est fourni (rétrocompat)
    resolved_from = from_date
    if resolved_from is None and days is not None:
        resolved_from = date.today() - timedelta(days=days)

    cotations = await crud.get_chart_data(
        db,
        action.id,
        from_date=resolved_from,
        to_date=to_date,
    )

    return [
        schemas.ChartData(
            date=c.date_seance,
            prix=c.prix,
            open=c.open,
            high=c.high,
            low=c.low,
            volume=c.volume,
        )
        for c in cotations
    ]
