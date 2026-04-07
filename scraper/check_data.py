import json
data = json.load(open('brvm_data.json', encoding='utf-8'))
print(f"Cotations: {len(data['cotations'])} actions")
print(f"Indices: {len(data['indices'])} indices")
for i in data['indices']:
    print(f"  {i['nom']}: {i['valeur']} ({i['variation']:+.2f}%)")
print(f"Capitalisation: {data['capitalisations'].get('capitalisation_actions', 'N/A')}")
