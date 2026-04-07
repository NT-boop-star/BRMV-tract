"""Verification Sikafinance data."""
import json

data = json.load(open('sikafinance_data.json', encoding='utf-8'))
lines = []

lines.append("=" * 60)
lines.append("  VERIFICATION SIKAFINANCE")
lines.append("=" * 60)

# Cotations
cot = data.get("cotations_aaz", [])
lines.append(f"\n  Cotations A-Z : {len(cot)} actions")
for c in cot[:5]:
    lines.append(f"    {c['nom']:30s} | {c['dernier']:>8} | {c['variation']:>+.2f}% | vol:{c['volume_titres']}")

# Indices
idx = data.get("indices_sectoriels", [])
lines.append(f"\n  Indices sectoriels : {len(idx)}")
for i in idx[:10]:
    v = i['valeur'] or 0
    var = i['variation'] or 0
    lines.append(f"    {i['nom']:35s} | {v:>10.2f} | {var:>+.2f}%")

# Palmares
pal = data.get("palmares", {})
h = pal.get("hausses", [])
lines.append(f"\n  Palmares hausses : {len(h)}")
for p in h[:5]:
    var = p['variation'] or 0
    lines.append(f"    {p['nom']:30s} | {p['dernier']:>8} | {var:>+.2f}% | vol:{p.get('volume','?')}")

# Dividendes
div = data.get("dividendes", [])
lines.append(f"\n  Dividendes : {len(div)}")
for d in div[:5]:
    m = d['montant_fcfa'] or 0
    r = d['rendement_pct'] or 0
    lines.append(f"    {d['nom']:25s} | {m:>8.2f} FCFA | {r:.2f}% | {d.get('date_detachement','?')}")

# Secteurs
sec = data.get("secteurs", [])
lines.append(f"\n  Secteurs : {len(sec)}")
for s in sec[:5]:
    vj = s.get('variation_jour') or 0
    vy = s.get('variation_ytd') or 0
    lines.append(f"    {s['nom']:30s} | Jour:{vj:>+.2f}% | YTD:{vy:>+.2f}%")

lines.append(f"\n{'=' * 60}")
lines.append("  [OK] Verification terminee")

with open("sika_verification.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Fichier sika_verification.txt cree")
