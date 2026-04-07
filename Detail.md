Type 1 — PDF texte natif
Généré directement depuis Word, Excel ou InDesign.
Texte sélectionnable et copiable.
pdfplumber extrait les données proprement.

Type 2 — PDF scanné
Document physique photographié puis sauvegardé en PDF.
C'est une image déguisée en PDF.
pdfplumber ne voit que des pixels — zéro texte.
→ Nécessite un pipeline OCR.


### Pipeline complet en 3 étapes


PDF reçu (natif ou scanné)
         ↓
ÉTAPE 1 : Détection automatique du type
→ PDF texte natif  → pdfplumber extraction directe
→ PDF scanné       → OCR (Tesseract ou Google Document AI)
         ↓
ÉTAPE 2 : Nettoyage et normalisation
→ Correction erreurs OCR courantes
→ Normalisation des chiffres (espaces, virgules, points)
→ Identification des sections (Bilan, Compte de résultat...)
         ↓
ÉTAPE 3 : Extraction structurée par LLM
→ Texte brut envoyé au modèle IA (Groq ou Gemini)
→ Extraction des valeurs en JSON strict
→ Validation logique comptable
→ Calcul automatique des ratios
         ↓
Données propres stockées en PostgreSQL

### Niveaux de fiabilité OCR

| Qualité du PDF | Fiabilité extraction | Action |
|---|---|---|
| PDF texte natif | ✅ Très haute | Extraction directe |
| Scan haute qualité ≥ 300 DPI | ✅ Haute | OCR Tesseract |
| Scan qualité correcte 150-300 DPI | ⚠️ Moyenne | OCR + validation LLM |
| Scan basse qualité < 150 DPI | ⚠️ Faible | Google Document AI |
| Scan très dégradé, pages tordues | ❌ Très faible | Saisie manuelle |

---

## Module IA — Architecture complète

### Principe fondamental — Zéro dépendance payante

L'ensemble du module IA repose sur des modèles
entièrement gratuits avec un système de fallback
à 3 niveaux. Si un service est indisponible ou
atteint sa limite, le suivant prend le relais
automatiquement et sans interruption.

### Les modèles disponibles gratuits

#### Gemini 2.0 Flash — Google AI Studio


URL     : aistudio.google.com (pas Vertex AI — gratuit)
Limite  : 1 500 requêtes / jour
Contexte: 1 million de tokens
Qualité : ⭐⭐⭐⭐⭐
Usage   : Principal — toutes les analyses


Important : Gemini 2.0 Flash via Google AI Studio
est GRATUIT. C'est Vertex AI (Google Cloud) qui est payant.
Ces deux services sont distincts.

#### Groq — Llama 3.3 70B


URL     : console.groq.com (gratuit)
Limite  : 1 000 requêtes / jour — 6 000 tokens/min
Vitesse : Exceptionnelle (le plus rapide du marché)
Qualité : ⭐⭐⭐⭐
Usage   : Backup principal + analyses rapides


#### OpenRouter — Modèles gratuits


URL     : openrouter.ai (gratuit)
Modèles gratuits disponibles :
  - meta-llama/llama-3.2-3b-instruct:free
  - mistralai/mistral-7b-instruct:free
  - deepseek/deepseek-r1:free
  - qwen/qwen-2.5-7b-instruct:free
Qualité : ⭐⭐⭐
Usage   : Backup secondaire
### Usage par fonctionnalité

| Fonctionnalité | Modèle principal | Backup | Fréquence |
|---|---|---|---|
| Extraction données PDF | Gemini 2.0 Flash | Groq | 1-2x/an par société |
| Recommandations profil | Gemini 2.0 Flash | Groq | Sur demande |
| Analyse conversationnelle | Gemini 2.0 Flash | Groq | Sur demande |
| Résumé marché hebdo | Gemini 2.0 Flash | Groq | 2x/semaine |
| Alertes intelligentes | Groq (rapidité) | Gemini | Événementiel |
| Comparateur actions | Gemini 2.0 Flash | Groq | Sur demande |

---

## Les 3 profils de risque

### Conservateur — Risque bas


Objectif    : Préservation capital + revenu dividende régulier
Horizon     : 3 à 5 ans minimum
Priorité    : Dividende stable et croissant sur 5 ans
Tolérance   : Faible volatilité uniquement


| Critère | Seuil |
|---|---|
| Rendement dividende | ≥ 5% |
| Payout Ratio | ≤ 70% |
| Dividende consécutif | ≥ 5 ans |
| PER | ≤ 10 |
| ROE moyen 5 ans | ≥ 12% |
| ROIC moyen 5 ans | ≥ 12% |
| Dette/EBITDA | ≤ 1.5x |
| FCF positif | ≥ 4 ans/5 |
| FCF yield | ≥ 5% |
| Marge de sécurité | ≥ 25% |
| Pays autorisés | CI, SN, BJ, TG |
| Secteurs prioritaires | Télécoms, Énergie, Services publics |
| Actions typiques | SNTS, ORAC, TTLC, CIE, SODECI |

### Modéré — Risque moyen


Objectif    : Équilibre dividende + appréciation capital
Horizon     : 5 à 7 ans
Priorité    : Croissance bénéfices + dividende régulier
Tolérance   : Fluctuations modérées acceptées


| Critère | Seuil |
|---|---|
| Rendement dividende | ≥ 3% |
| Payout Ratio | ≤ 75% |
| Dividende consécutif | ≥ 3 ans |
| PER | ≤ 14 |
| ROE moyen 5 ans | ≥ 10% |
| ROIC moyen 5 ans | ≥ 10% |
| Dette/EBITDA | ≤ 2.5x |
| FCF positif | ≥ 3 ans/5 |
| FCF yield | ≥ 3% |
| Marge de sécurité | ≥ 15% |
| Pays autorisés | CI, SN, BJ, TG |
| Secteurs prioritaires | Finance, Distribution, Industrie |
| Actions typiques | SGBC, BOAC, NSBC, ETIT, SLBC |

### Agressif — Risque élevé


Objectif    : Maximiser l'appréciation du capital
Horizon     : 7 à 10 ans minimum
Priorité    : Croissance forte des bénéfices
Tolérance   : Haute volatilité, dividende non prioritaire


| Critère | Seuil |
|---|---|
| PER normalisé 5 ans | ≤ 15 |
| PBR | ≤ 3 |
| ROE moyen 3 ans | ≥ 8% |
| ROIC moyen 3 ans | ≥ 8% |
| Dette/EBITDA | ≤ 3.5x |
| FCF positif | ≥ 2 ans/5 |
| Croissance BN 3 ans | ≥ 12% |
| Marge de sécurité | ≥ 10% |
| Catalyseurs macro | Obligatoires |
| Pays autorisés | Tous (risque compris) |
| Secteurs prioritaires | Agro-industrie, Finance émergente |
| Actions typiques | SAPH, PALC, SOGC, SPHC, SICC |

---

## Ratios financiers calculés

Tous extraits des rapports annuels PDF (brvm.org — gratuit)
via le pipeline OCR + LLM.
Identiques à richbourse premium — même source, même calcul.

| Ratio | Formule | Fréquence |
|---|---|---|
| BPA | Résultat Net ÷ Nombre d'actions | Annuelle |
| PER | Prix ÷ BPA | Temps réel prix + annuelle BPA |
| PER normalisé | Prix ÷ (BN moyen 5 ans ÷ Nb actions) | Annuelle |
| ROE | Résultat Net ÷ Capitaux Propres | Annuelle |
| ROIC | NOPAT ÷ Capital Investi | Annuelle |
| PBR | Prix ÷ (Capitaux Propres ÷ Nb actions) | Temps réel |
| Rendement | Dividende Net ÷ Prix | Temps réel |
| Payout Ratio | Dividende versé ÷ Bénéfice Net | Annuelle |
| FCF | Flux exploitation - Capex | Annuelle |
| FCF yield | FCF ÷ Capitalisation boursière | Temps réel |
| Dette nette / EBITDA | Dette Nette ÷ EBITDA | Annuelle |
| Marge nette | Résultat Net ÷ CA | Annuelle |
| TCAM CA 5 ans | Croissance annuelle composée CA | Annuelle |
| TCAM BN 5 ans | Croissance annuelle composée BN | Annuelle |
| Marge de sécurité | (VI - Prix) ÷ VI | Temps réel |

---

## Score de sélection — Paramètres complets (0 à 100)

### Filtres éliminatoires absolus


❌ Payout Ratio > 100%
❌ FCF négatif 4 années sur 5
❌ Résultat net négatif 2 années consécutives
❌ BPA en déclin 3 années consécutives
❌ ROIC < WACC 3 années consécutives
❌ Dette nette / EBITDA > 5x (hors banques)
❌ NPL Ratio > 10% (banques uniquement)
❌ Dividende coupé l'année précédente sans justification
❌ Rapport annuel non publié depuis > 18 mois
❌ Réserves ou avertissements graves dans rapport d'audit
❌ Volume moyen < seuil minimum sur 3 mois
❌ Fréquence cotation < 60% des séances
❌ Rendement total attendu < taux sans risque + 3%


### Tableau des niveaux de scoring

| Niveau | Critère | Points max |
|---|---|---|
| 1 | Liquidité | 20 |
| 2 | Free Cash Flow | 20 |
| 3 | Qualité bénéfices + BPA + dilution | 25 |
| 4 | ROIC | 10 |
| 5 | Qualité du dividende | 20 |
| 6 | Solidité du bilan + ROE croisé | 20 |
| 7 | Valorisation + Marge de sécurité | 20 |
| 8 | Rendement vs taux sans risque | 5 |
| 9 | Position concurrentielle | 10 |
| 10 | Contexte macro pays | 15 |
| 11 | Gouvernance | 10 |
| 12 | Matières premières (agro uniquement) | 10 |
| **TOTAL** | | **175 → ramené sur 100** |

### Interprétation du score

| Score | Interprétation | Action IA |
|---|---|---|
| 80 - 100 | Excellent — Très compatible profil | ✅ Recommander en priorité |
| 65 - 79 | Bon — Compatible avec réserves | ✅ Recommander avec nuances |
| 50 - 64 | Moyen — Potentiel mais vigilance | ⚠️ Surveiller |
| 35 - 49 | Faible — Risques identifiés | ❌ Ne pas recommander |
| < 35 | Très faible — À éviter | ❌ Exclure |

---

## Règles sectorielles

### Télécoms (SNTS, ORAC)


✓ Marge EBITDA         ≥ 30%
✓ Capex / CA           ≤ 20%
✓ FCF yield            ≥ 5%
✓ Croissance ARPU      Stable ou positive


### Banques (SGBC, BOAC, NSBC, ETIT, BICICI...)


✓ Tier 1 Capital Ratio ≥ 8%     (pas Dette/EBITDA)
✓ NPL Ratio            ≤ 5%
✓ Couverture NPL       ≥ 80%
✓ NIM                  ≥ 4%
✓ Croissance crédits   ≥ 5% sur 3 ans
✓ ROE                  ≥ 12%


### Agro-industriels (SAPH, PALC, SOGB, SPHC, SIFCA)


✓ PBR plutôt que PER (cycliques)
✓ Position cycle matière = critère principal
✓ Bilan solide en bas de cycle = éliminatoire si non
✓ PER normalisé 5 ans (jamais instantané)
✓ Dette/EBITDA         ≤ 2x
✓ ROIC calculé sur cycle complet


### Utilities (CIE, SODECI)


✓ Contrat État valide  = éliminatoire si absent
✓ Rendement dividende  ≥ 5%
✓ Payout               ≤ 80% (tolérance flux stables)
✓ Dette/EBITDA         ≤ 4x (tolérance flux prévisibles)
✓ FCF yield            ≥ 3% (tolérance Capex élevés)


---

## Alertes dégradantes automatiques


SCORE -10 POINTS
- FCF en déclin 3 années consécutives
- CA +10% mais BN en déclin = compression sévère
- BN +10% mais BPA stable = dilution significative
- ROIC en déclin régulier sur 3 ans
- Retard publication rapport annuel > 12 mois

SCORE -8 POINTS
- ROE élevé mais Dette/EBITDA > 3x (ROE artificiel)
- FCF ne couvre pas le dividende (FCF/Div < 1.0x)
- Volume en déclin 3 mois même au-dessus du seuil

SCORE -5 POINTS
- Payout Ratio entre 80% et 100%
- Marge nette en déclin 3 ans consécutifs
- Changement de dirigeant non expliqué dans l'année
- Dépendance > 50% revenus à un client ou contrat
- Dividende yield > 12% (vérifier yield trap)

SCORE -3 POINTS
- Nouveau concurrent majeur entrant sur le marché
- Parts de marché en déclin 2 ans consécutifs
- Disruption technologique identifiée sur le secteur
- Exposition > 30% dans un pays à stabilité ≤ 2/5


---

## Analyse technique

### Réalité de la BRVM

La BRVM cote 2x par semaine (lundi et vendredi).
47 actions dont 10 à 15 ont une liquidité suffisante
pour que l'analyse technique soit fiable.
Pour un investisseur long terme l'analyse technique
est un outil secondaire — les fondamentaux priment.

Actions liquides (analyse technique fiable) :
SNTS, ORAC, SGBC, ETIT, BOAC, TTLC, SLBC, NSBC, PALC, SPHC

### Construction de l'historique

- Phase 1 : Parser les BOC PDF archivés (rétroactif)
- Phase 2 : Scraper automatiquement chaque séance (prospectif)
- Minimum requis : 200 séances ≈ 2 ans pour MA200

### Indicateurs disponibles (Close + Volume)

| Indicateur | Disponible | Pertinence long terme |
|---|---|---|
| MA 20, 50, 200 | ✅ | Faible — point d'entrée |
| MACD | ✅ | Faible — actions liquides |
| RSI 14 | ✅ | Faible — zones extrêmes |
| Bollinger Bands | ✅ | Faible — survente/surachat |
| Anomalies de volume | ✅ | Moyen — signal d'activité |
| Plus hauts / bas N jours | ✅ | Moyen — niveaux clés |

---

Pour les pdf des etats financiers il y'a chaque action qui des publications appelles bilan financier ou bilan annuel c'est eux on va extrait 