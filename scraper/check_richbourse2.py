"""Verification des donnees Richbourse - sortie fichier UTF-8."""
import json

data = json.load(open('richbourse_data.json', encoding='utf-8'))
lines = []

lines.append("=" * 60)
lines.append("  VERIFICATION RICHBOURSE")
lines.append("=" * 60)

variations = data.get("variations", [])
lines.append(f"\n  Variations : {len(variations)} actions")
if variations:
    lines.append("  Top 5 :")
    for v in variations[:5]:
        var = v.get('variation', 0) or 0
        prix = v.get('cours_actuel', 0) or 0
        lines.append(f"    {v['ticker']:8s} | {v['nom']:15s} | {prix:>8} FCFA | {var:>+.2f}%")

dividendes = data.get("dividendes", [])
lines.append(f"\n  Dividendes : {len(dividendes)} societes")
for d in dividendes:
    div = d.get('dividende_fcfa', 0) or 0
    rend = d.get('rendement_pct', 0) or 0
    ex = d.get('date_ex_dividende') or '(inconnue)'
    pai = d.get('date_paiement') or '(inconnue)'
    lines.append(f"    {d['societe']:20s} | {div:>8.2f} FCFA | Rend:{rend:.2f}% | Ex:{ex} | Pai:{pai}")

actualites = data.get("actualites", [])
lines.append(f"\n  Actualites : {len(actualites)} articles")
for a in actualites[:5]:
    lines.append(f"    - {a['titre'][:65]}")

notations = data.get("notations", [])
lines.append(f"\n  Notations : {len(notations)} notations")
for n in notations[:5]:
    lines.append(f"    {n['ticker']:6s} | {n['agence']:25s} | {n['date_notation']:15s} | CT:{n['note_court_terme']} LT:{n['note_long_terme']}")

lines.append(f"\n{'=' * 60}")
lines.append("  [OK] Verification terminee")

with open("rb_verification.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Fichier rb_verification.txt cree")
