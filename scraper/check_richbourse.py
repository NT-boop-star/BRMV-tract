"""Verification des donnees Richbourse scrappees."""
import sys, io
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import json

data = json.load(open('richbourse_data.json', encoding='utf-8'))

print("=" * 55)
print("  VERIFICATION RICHBOURSE")
print("=" * 55)

# Variations
variations = data.get("variations", [])
print(f"\n  Variations : {len(variations)} actions")
if variations:
    print("  Top 5 :")
    for v in variations[:5]:
        var = v.get('variation', 0) or 0
        prix = v.get('cours_actuel', 0) or 0
        cap = v.get('capitalisation', 0) or 0
        print(f"    {v['ticker']:8s} | {v['nom']:15s} | {prix:>8} FCFA | {var:>+.2f}% | Cap: {cap:>15,}")

# Dividendes
dividendes = data.get("dividendes", [])
print(f"\n  Dividendes : {len(dividendes)} societes")
if dividendes:
    for d in dividendes:
        div = d.get('dividende_fcfa', 0) or 0
        rend = d.get('rendement_pct', 0) or 0
        ex = d.get('date_ex_dividende') or '(inconnue)'
        pai = d.get('date_paiement') or '(inconnue)'
        print(f"    {d['societe']:20s} | {div:>8.2f} FCFA | Rend: {rend:.2f}% | Ex: {ex} | Pai: {pai}")

# Actualites
actualites = data.get("actualites", [])
print(f"\n  Actualites : {len(actualites)} articles")
if actualites:
    print("  5 dernieres :")
    for a in actualites[:5]:
        titre = a['titre'][:60]
        print(f"    - {titre}")

# Notations
notations = data.get("notations", [])
print(f"\n  Notations : {len(notations)} notations")
if notations:
    print("  Exemples :")
    for n in notations[:5]:
        print(f"    {n['ticker']:8s} | {n['agence']:25s} | {n['date_notation']:15s} | CT: {n['note_court_terme']} | LT: {n['note_long_terme']}")

print(f"\n{'=' * 55}")
print("  [OK] Verification terminee")
print("=" * 55)
