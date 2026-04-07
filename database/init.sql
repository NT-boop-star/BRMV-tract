CREATE EXTENSION IF NOT EXISTS timescaledb;

-- TABLES CLASSIQUES
CREATE TABLE IF NOT EXISTS pays (
    id SERIAL PRIMARY KEY,
    code_iso2 VARCHAR(2) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS secteurs (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS actions (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) UNIQUE NOT NULL,
    nom VARCHAR(255) NOT NULL,
    secteur_id INTEGER REFERENCES secteurs(id),
    pays_id INTEGER REFERENCES pays(id),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS indices (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS seances (
    id SERIAL PRIMARY KEY,
    date_seance DATE UNIQUE NOT NULL,
    est_ferie BOOLEAN DEFAULT FALSE,
    volume_total BIGINT
);

CREATE TABLE IF NOT EXISTS rapports_annuels (
    id SERIAL PRIMARY KEY,
    action_id INTEGER REFERENCES actions(id),
    annee INTEGER NOT NULL,
    ca DECIMAL(15, 2),
    resultat_net DECIMAL(15, 2),
    capitaux_propres DECIMAL(15, 2),
    dette_nette DECIMAL(15, 2),
    ebitda DECIMAL(15, 2),
    flux_exploitation DECIMAL(15, 2),
    capex DECIMAL(15, 2),
    fcf DECIMAL(15, 2),
    UNIQUE(action_id, annee)
);

CREATE TABLE IF NOT EXISTS dividendes (
    id SERIAL PRIMARY KEY,
    action_id INTEGER REFERENCES actions(id),
    annee_exercice INTEGER,
    date_ex_dividende DATE,
    date_paiement DATE,
    montant_net DECIMAL(10, 2) NOT NULL,
    rendement_calcul DECIMAL(10, 2),
    payout_ratio DECIMAL(5, 2),
    UNIQUE (action_id, date_paiement, montant_net)
);

CREATE TABLE IF NOT EXISTS notations (
    id SERIAL PRIMARY KEY,
    action_id INTEGER REFERENCES actions(id),
    agence VARCHAR(100) NOT NULL,
    date_notation VARCHAR(50),
    note_court_terme VARCHAR(50),
    note_long_terme VARCHAR(50),
    UNIQUE(action_id, agence, date_notation)
);

CREATE TABLE IF NOT EXISTS indicateurs_macro (
    id SERIAL PRIMARY KEY,
    pays_id INTEGER REFERENCES pays(id),
    annee INTEGER,
    croissance_pib DECIMAL(5, 2),
    inflation DECIMAL(5, 2),
    taux_bancarisation DECIMAL(5, 2),
    taux_urbanisation DECIMAL(5, 2)
);

CREATE TABLE IF NOT EXISTS matieres_premieres (
    id SERIAL PRIMARY KEY,
    symbole VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    unite VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    action_id INTEGER REFERENCES actions(id),
    date_publication TIMESTAMP NOT NULL,
    titre VARCHAR(255) NOT NULL,
    url VARCHAR(500) UNIQUE NOT NULL,
    provenance VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS logs_collecte (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50),
    statut VARCHAR(20),
    lignes_inserees INTEGER,
    erreur TEXT
);

-- TABLES HYPERTABLES (Time-Series Metrics)
CREATE TABLE IF NOT EXISTS cotations (
    date_seance DATE NOT NULL,
    action_id INTEGER REFERENCES actions(id),
    prix INTEGER NOT NULL,
    variation DECIMAL(5, 2),
    volume INTEGER
);
SELECT create_hypertable('cotations', 'date_seance', if_not_exists => TRUE);
-- L'index unique garantit une ligne max par action et par jour
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_cotations ON cotations(date_seance, action_id);

CREATE TABLE IF NOT EXISTS cotations_indices (
    date_seance DATE NOT NULL,
    indice_id INTEGER REFERENCES indices(id),
    valeur DECIMAL(10, 2) NOT NULL,
    variation DECIMAL(5, 2)
);
SELECT create_hypertable('cotations_indices', 'date_seance', if_not_exists => TRUE);
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_cotations_indices ON cotations_indices(date_seance, indice_id);

CREATE TABLE IF NOT EXISTS indicateurs_techniques (
    date_seance DATE NOT NULL,
    action_id INTEGER REFERENCES actions(id),
    rsi_14 DECIMAL(5, 2),
    macd DECIMAL(10, 2),
    ma_20 DECIMAL(10, 2),
    ma_50 DECIMAL(10, 2),
    ma_200 DECIMAL(10, 2)
);
SELECT create_hypertable('indicateurs_techniques', 'date_seance', if_not_exists => TRUE);
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_ind_tech ON indicateurs_techniques(date_seance, action_id);

CREATE TABLE IF NOT EXISTS ratios (
    date_calcul DATE NOT NULL,
    action_id INTEGER REFERENCES actions(id),
    per DECIMAL(10, 2),
    roe DECIMAL(10, 2),
    pbr DECIMAL(10, 2),
    fcf_yield DECIMAL(5, 2)
);
SELECT create_hypertable('ratios', 'date_calcul', if_not_exists => TRUE);
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_ratios ON ratios(date_calcul, action_id);

CREATE TABLE IF NOT EXISTS prix_matieres_premieres (
    date_prix DATE NOT NULL,
    matiere_id INTEGER REFERENCES matieres_premieres(id),
    prix DECIMAL(10, 2) NOT NULL
);
SELECT create_hypertable('prix_matieres_premieres', 'date_prix', if_not_exists => TRUE);
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_matieres ON prix_matieres_premieres(date_prix, matiere_id);

CREATE TABLE IF NOT EXISTS cotations_secteurs (
    date_seance DATE NOT NULL,
    secteur_id INTEGER REFERENCES secteurs(id),
    ouverture DECIMAL(15, 2),
    plus_haut DECIMAL(15, 2),
    plus_bas DECIMAL(15, 2),
    dernier DECIMAL(15, 2),
    variation_jour DECIMAL(10, 2),
    variation_ytd DECIMAL(10, 2),
    volume BIGINT
);
SELECT create_hypertable('cotations_secteurs', 'date_seance', if_not_exists => TRUE);
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_cotations_secteurs ON cotations_secteurs(date_seance, secteur_id);

-- VUE MATERIALISÉE POUR LE DASHBOARD (Optimisée)
CREATE MATERIALIZED VIEW vue_derniers_cours AS
SELECT 
    c.action_id,
    a.ticker,
    c.prix,
    c.variation,
    c.date_seance
FROM cotations c
JOIN actions a ON c.action_id = a.id
WHERE c.date_seance = (SELECT MAX(date_seance) FROM cotations);
