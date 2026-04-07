

## Ce qui reste à implémenter ❌

### Priorité 1 — Fondamentaux (cœur du projet)

```
Pipeline PDF complet
→ Détection natif vs scanné
→ OCR Tesseract pour PDFs scannés
→ Extraction structurée via LLM (Groq ou Gemini)
→ Validation logique comptable automatique
→ Calcul ROIC, FCF, BPA, Marge de sécurité sur 5 ans
→ Indicateurs sectoriels (banques, agro, télécoms, utilities)

Ratios calculés automatiquement
→ PER normalisé 5 ans (pas instantané)
→ ROIC = NOPAT / Capital Investi
→ FCF yield = FCF / Capitalisation
→ Payout Ratio = Dividende / BN
→ Marge de sécurité = (VI - Prix) / VI
→ BPA + surveillance dilution
→ Dette/EBITDA
→ Croissance TCAM CA et BN sur 5 ans
```

---

### Priorité 2 — Module IA complet

```
IAClient avec fallback 4 niveaux
→ Gemini 2.0 Flash (principal — gratuit)
→ Groq Llama 3.3 70B (backup 1)
→ OpenRouter (backup 2)
→ Ollama local (backup 3)

Quiz de personnalisation (5 questions)
→ Horizon, objectif, montant, exclusions secteur/pays

Screener avec filtres éliminatoires automatiques
→ 13 filtres éliminatoires (payout > 100%, FCF négatif...)
→ Score 0-100 calculé sur 175 points

Recommandations par profil
→ 3 profils (Conservateur / Modéré / Agressif)
→ Indicateurs spécifiques par secteur
  (banques : Tier1/NPL/NIM, agro : PBR + cycle matière,
   utilities : contrat État, télécoms : marge EBITDA)
→ Thèse investissement long terme argumentée
→ Marge de sécurité calculée
→ ROIC vs WACC analysé
→ Nombre de titres achetables selon montant

Analyse conversationnelle libre
→ Questions libres sur les actions et le marché

Comparateur long terme
→ 2 actions côte à côte sur tous les critères

Résumé mensuel automatique du portefeuille
```

---

### Priorité 3 — Données manquantes

```
BCEAO — DBnomics
→ Taux directeur (tendance)
→ M1 / M2 / M3
→ Crédits à l'économie
→ Inflation IPCH par pays

FMI
→ Prévisions PIB pays UEMOA

Richbourse complémentaire
→ Dividendes structurés
→ Notations financières

Indicateurs macro supplémentaires
→ Taux bancarisation (Banque Mondiale)
→ Taux urbanisation + tendance
→ Pénétration mobile
→ Croissance démographique
```

---

### Priorité 4 — Alertes intelligentes

```
Déclencheurs à implémenter :
→ Résultats annuels publiés → recalcul score
→ Dividende coupé ou augmenté → alerte
→ Changement taux BCEAO → impact banques
→ Variation matière > 10% → impact agro
→ Score baisse > 10 points → alerte révision
→ Instabilité politique détectée via news

Canaux de notification :
→ Email
→ SMS (cité dans ton document comme prochaine étape)
→ Notification web push
```

---

### Priorité 5 — Données historiques BOC

```
Parser BOC PDF rétroactif
→ Archives brvm.org depuis 2018+
→ Construction historique Close + Volume
→ Minimum 200 séances pour MA200
→ Base TimescaleDB alimentée

Note : les chandeliers japonais sont déjà sur le frontend
mais nécessitent Open/High/Low qui ne viennent pas
du BOC standard — à clarifier si cette donnée existe
quelque part ou si c'est Close uniquement.
```

---

