from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, Date, MetaData, TIMESTAMP, BigInteger
from sqlalchemy.orm import relationship
from database import Base

metadata = MetaData()

class Secteur(Base):
    __tablename__ = "secteurs"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), unique=True, nullable=False)
    
    actions = relationship("Action", back_populates="secteur")

class RapportAnnuel(Base):
    __tablename__ = "rapports_annuels"
    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(Integer, ForeignKey("actions.id"))
    annee = Column(Integer, nullable=False)
    ca = Column(Numeric(20, 2))
    resultat_net = Column(Numeric(20, 2))
    capitaux_propres = Column(Numeric(20, 2))
    dette_nette = Column(Numeric(20, 2))
    ebitda = Column(Numeric(20, 2))
    flux_exploitation = Column(Numeric(20, 2))
    capex = Column(Numeric(20, 2))
    fcf = Column(Numeric(20, 2))

    action = relationship("Action", back_populates="rapports_annuels")

class Action(Base):
    __tablename__ = "actions"
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), unique=True, nullable=False)
    nom = Column(String(255), nullable=False)
    secteur_id = Column(Integer, ForeignKey("secteurs.id"))
    pays_id = Column(Integer) # ForeignKey non definie strict ici pour alleger si non utilisee
    is_active = Column(Boolean, default=True)

    secteur = relationship("Secteur", back_populates="actions")
    cotations = relationship("Cotation", back_populates="action")
    dividendes = relationship("Dividende", back_populates="action")
    notations = relationship("Notation", back_populates="action")
    news = relationship("News", back_populates="action")
    rapports_annuels = relationship("RapportAnnuel", back_populates="action")

class Indice(Base):
    __tablename__ = "indices"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), unique=True, nullable=False)
    description = Column(String)

class Cotation(Base):
    __tablename__ = "cotations"
    date_seance = Column(Date, primary_key=True)
    action_id = Column(Integer, ForeignKey("actions.id"), primary_key=True)
    prix = Column(Integer, nullable=False)  # prix de clôture
    open = Column(Integer)                  # prix d'ouverture
    high = Column(Integer)                  # plus haut de la séance
    low = Column(Integer)                   # plus bas de la séance
    variation = Column(Numeric(5, 2))
    volume = Column(Integer)

    action = relationship("Action", back_populates="cotations")

class CotationIndice(Base):
    __tablename__ = "cotations_indices"
    date_seance = Column(Date, primary_key=True)
    indice_id = Column(Integer, ForeignKey("indices.id"), primary_key=True)
    valeur = Column(Numeric(10, 2), nullable=False)
    variation = Column(Numeric(5, 2))

class CotationSecteur(Base):
    __tablename__ = "cotations_secteurs"
    date_seance = Column(Date, primary_key=True)
    secteur_id = Column(Integer, ForeignKey("secteurs.id"), primary_key=True)
    ouverture = Column(Numeric(15, 2))
    plus_haut = Column(Numeric(15, 2))
    plus_bas = Column(Numeric(15, 2))
    dernier = Column(Numeric(15, 2))
    variation_jour = Column(Numeric(10, 2))
    variation_ytd = Column(Numeric(10, 2))
    volume = Column(BigInteger)

class Dividende(Base):
    __tablename__ = "dividendes"
    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(Integer, ForeignKey("actions.id"))
    annee_exercice = Column(Integer)
    date_ex_dividende = Column(Date)
    date_paiement = Column(Date)
    montant_net = Column(Numeric(10, 2), nullable=False)
    rendement_calcul = Column(Numeric(10, 2))
    payout_ratio = Column(Numeric(5, 2))

    action = relationship("Action", back_populates="dividendes")

class Notation(Base):
    __tablename__ = "notations"
    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(Integer, ForeignKey("actions.id"))
    agence = Column(String(100), nullable=False)
    date_notation = Column(String(50))
    note_court_terme = Column(String(50))
    note_long_terme = Column(String(50))

    action = relationship("Action", back_populates="notations")

class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(Integer, ForeignKey("actions.id"))
    date_publication = Column(TIMESTAMP, nullable=False)
    titre = Column(String(255), nullable=False)
    url = Column(String(500), unique=True, nullable=False)
    provenance = Column(String(50))

    action = relationship("Action", back_populates="news")

class Pays(Base):
    __tablename__ = "pays"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), unique=True, nullable=False)
    code = Column(String(5), unique=True, nullable=False)
    
    indicateurs = relationship("IndicateurMacro", back_populates="pays")

class IndicateurMacro(Base):
    __tablename__ = "indicateurs_macro"
    id = Column(Integer, primary_key=True, index=True)
    pays_id = Column(Integer, ForeignKey("pays.id"))
    annee = Column(Integer, nullable=False)
    croissance_pib = Column(Numeric(5, 2))
    inflation = Column(Numeric(5, 2))
    taux_bancarisation = Column(Numeric(5, 2))
    population = Column(BigInteger)
    
    pays = relationship("Pays", back_populates="indicateurs")

class MatierePremiere(Base):
    __tablename__ = "matieres_premieres"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), unique=True, nullable=False)
    symbole = Column(String(10), unique=True)
    unite = Column(String(20))
    
    prix = relationship("PrixMatierePremiere", back_populates="matiere")

class PrixMatierePremiere(Base):
    __tablename__ = "prix_matieres_premieres"
    date_jour = Column(Date, primary_key=True)
    matiere_id = Column(Integer, ForeignKey("matieres_premieres.id"), primary_key=True)
    prix = Column(Numeric(15, 2), nullable=False)
    variation_jour = Column(Numeric(5, 2))
    
    matiere = relationship("MatierePremiere", back_populates="prix")
