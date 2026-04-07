from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from sqlalchemy.orm import selectinload
from datetime import date as date_type

import models

async def get_all_actions(db: AsyncSession):
    query = select(models.Action).options(selectinload(models.Action.secteur)).where(models.Action.is_active == True).order_by(models.Action.ticker)
    result = await db.execute(query)
    return result.scalars().all()

async def get_action_by_ticker(db: AsyncSession, ticker: str):
    query = select(models.Action).options(selectinload(models.Action.secteur)).where(models.Action.ticker == ticker.upper())
    result = await db.execute(query)
    return result.scalars().first()

async def get_derniere_cotation(db: AsyncSession, action_id: int):
    query = select(models.Cotation).where(models.Cotation.action_id == action_id).order_by(desc(models.Cotation.date_seance)).limit(1)
    result = await db.execute(query)
    return result.scalars().first()

async def get_dividendes_action(db: AsyncSession, action_id: int):
    query = select(models.Dividende).where(models.Dividende.action_id == action_id).order_by(desc(models.Dividende.date_ex_dividende), desc(models.Dividende.date_paiement))
    result = await db.execute(query)
    return result.scalars().all()

async def get_rapports_annuels_action(db: AsyncSession, action_id: int):
    query = select(models.RapportAnnuel).where(models.RapportAnnuel.action_id == action_id).order_by(desc(models.RapportAnnuel.annee))
    result = await db.execute(query)
    return result.scalars().all()

async def get_notations_action(db: AsyncSession, action_id: int):
    query = select(models.Notation).where(models.Notation.action_id == action_id)
    result = await db.execute(query)
    return result.scalars().all()

async def get_news_action(db: AsyncSession, action_id: int, limit: int = 10):
    query = select(models.News).where(models.News.action_id == action_id).order_by(desc(models.News.date_publication)).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_chart_data(
    db: AsyncSession,
    action_id: int,
    from_date: date_type = None,
    to_date: date_type = None,
):
    """
    Retourne l'historique des cotations filtré par plage de dates.
    Si from_date est None, remonte jusqu'au 01/01/2000.
    Si to_date est None, utilise la date du jour.
    """
    if from_date is None:
        from_date = date_type(2000, 1, 1)
    if to_date is None:
        to_date = date_type.today()

    conditions = [
        models.Cotation.action_id == action_id,
        models.Cotation.date_seance >= from_date,
        models.Cotation.date_seance <= to_date,
    ]
    query = (
        select(models.Cotation)
        .where(and_(*conditions))
        .order_by(models.Cotation.date_seance)  # ordre chronologique direct
    )
    result = await db.execute(query)
    return result.scalars().all()

async def get_screener(db: AsyncSession):
    # Chercher la date de la derniere seance pour filtrer les cotations du jour
    date_query = select(func.max(models.Cotation.date_seance))
    latest_date_res = await db.execute(date_query)
    latest_date = latest_date_res.scalar()

    if not latest_date:
        return []

    query = (
        select(models.Action.ticker, models.Action.nom, models.Secteur.nom.label("secteur"), models.Cotation.prix, models.Cotation.variation, models.Cotation.volume)
        .join(models.Cotation, models.Action.id == models.Cotation.action_id)
        .outerjoin(models.Secteur, models.Action.secteur_id == models.Secteur.id)
        .where(models.Cotation.date_seance == latest_date)
    )
    result = await db.execute(query)
    rows = result.all()
    
    # Formatage pour le BaseModel Pydantic
    return [
        {
            "ticker": r.ticker,
            "nom": r.nom,
            "secteur": r.secteur,
            "prix": r.prix,
            "variation": float(r.variation) if r.variation is not None else 0.0,
            "volume": r.volume or 0,
            "rendement_estime": None # A calculer ulterieurement
        }
        for r in rows
    ]

async def get_market_summary(db: AsyncSession):
    # Trouver la date la plus recente dans cotations_indices
    date_query = select(func.max(models.CotationIndice.date_seance))
    latest_date_res = await db.execute(date_query)
    latest_date = latest_date_res.scalar()

    if not latest_date:
        return None

    # Recuperer les indices
    idx_query = select(models.Indice.nom, models.CotationIndice.valeur, models.CotationIndice.variation).join(models.CotationIndice, models.Indice.id == models.CotationIndice.indice_id).where(models.CotationIndice.date_seance == latest_date)
    idx_res = await db.execute(idx_query)
    indices = [{"nom": r.nom, "valeur": float(r.valeur), "variation": float(r.variation)} for r in idx_res.all()]

    # Volume global de la seance
    vol_query = select(func.sum(models.Cotation.volume)).where(models.Cotation.date_seance == latest_date)
    vol_res = await db.execute(vol_query)
    volume_global = vol_res.scalar() or 0

    return latest_date, indices, volume_global

async def get_all_news(db: AsyncSession, limit: int = 50, offset: int = 0):
    query = (
        select(models.News, models.Action.ticker, models.Action.nom.label("action_nom"))
        .outerjoin(models.Action, models.News.action_id == models.Action.id)
        .order_by(desc(models.News.date_publication))
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(query)
    rows = result.all()
    
    # Format the results to include ticker/action name
    return [
        {
            "id": r.News.id,
            "date_publication": r.News.date_publication.isoformat() if r.News.date_publication else None,
            "titre": r.News.titre,
            "url": r.News.url,
            "provenance": r.News.provenance,
            "ticker": r.ticker,
            "action_nom": r.action_nom,
        }
        for r in rows
    ]

async def get_sector_performance(db: AsyncSession):
    # Chercher la date de la derniere seance
    date_query = select(func.max(models.Cotation.date_seance))
    latest_date_res = await db.execute(date_query)
    latest_date = latest_date_res.scalar()

    if not latest_date:
        return []

    # Agreger par secteur
    # On joint Cotation, Action et Secteur
    query = (
        select(
            models.Secteur.nom.label("secteur"),
            func.sum(models.Cotation.volume).label("volume_total"),
            func.avg(models.Cotation.variation).label("variation_moyenne"),
            func.count(models.Action.id).label("nb_actions")
        )
        .join(models.Action, models.Secteur.id == models.Action.secteur_id)
        .join(models.Cotation, models.Action.id == models.Cotation.action_id)
        .where(models.Cotation.date_seance == latest_date)
        .group_by(models.Secteur.nom)
    )
    
    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "secteur": r.secteur,
            "volume_total": r.volume_total or 0,
            "variation_moyenne": float(r.variation_moyenne) if r.variation_moyenne is not None else 0.0,
            "nb_actions": r.nb_actions
        }
        for r in rows
    ]
