from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

# --- Schemas Secteurs ---
class SecteurBase(BaseModel):
    id: int
    nom: str

    class Config:
        from_attributes = True

# --- Schemas Actions ---
class ActionBase(BaseModel):
    id: int
    ticker: str
    nom: str
    secteur_id: Optional[int]

    class Config:
        from_attributes = True

class ActionWithSecteur(ActionBase):
    secteur: Optional[SecteurBase] = None

# --- Schemas Cotations ---
class CotationBase(BaseModel):
    date_seance: date
    prix: int
    open: Optional[int] = None
    high: Optional[int] = None
    low: Optional[int] = None
    variation: Optional[float]
    volume: Optional[int]

    class Config:
        from_attributes = True

class ChartData(BaseModel):
    date: date
    prix: int
    open: Optional[int] = None
    high: Optional[int] = None
    low: Optional[int] = None
    volume: Optional[int]

# --- Schemas Dividendes & Notations ---
class DividendeBase(BaseModel):
    annee_exercice: Optional[int]
    date_ex_dividende: Optional[date]
    date_paiement: Optional[date]
    montant_net: float
    rendement_calcul: Optional[float]
    payout_ratio: Optional[float]

    class Config:
        from_attributes = True

class RapportAnnuelBase(BaseModel):
    annee: int
    ca: Optional[float]
    resultat_net: Optional[float]
    capitaux_propres: Optional[float]
    dette_nette: Optional[float]
    ebitda: Optional[float]
    flux_exploitation: Optional[float]
    capex: Optional[float]
    fcf: Optional[float]

    class Config:
        from_attributes = True

class NotationBase(BaseModel):
    agence: str
    date_notation: Optional[str]
    note_court_terme: Optional[str]
    note_long_terme: Optional[str]

    class Config:
        from_attributes = True

class NewsBase(BaseModel):
    date_publication: datetime
    titre: str
    url: str
    provenance: Optional[str]

    class Config:
        from_attributes = True

# --- Reponse Details Action ---
class ActionDetailResponse(BaseModel):
    action: ActionWithSecteur
    derniere_cotation: Optional[CotationBase]
    dividendes: List[DividendeBase]
    notations: List[NotationBase]
    news: List[NewsBase]
    rapports_annuels: List[RapportAnnuelBase] = []

# --- Screener (Tableau complet) ---
class ScreenerRow(BaseModel):
    ticker: str
    nom: str
    secteur: Optional[str]
    prix: int
    variation: float
    volume: int
    rendement_estime: Optional[float]
    # per, pbr etc. pourraient etre ajoutes plus tard

    class Config:
        from_attributes = True

# --- Market Summary ---
class MarketIndex(BaseModel):
    nom: str
    valeur: float
    variation: float

class MarketSummary(BaseModel):
    date_maj: date
    indices: List[MarketIndex]
    volume_global: int
    top_hausses: List[ScreenerRow]
    top_baisses: List[ScreenerRow]

# --- Sector Analysis ---
class SectorPerformance(BaseModel):
    secteur: str
    volume_total: int
    variation_moyenne: float
    nb_actions: int
