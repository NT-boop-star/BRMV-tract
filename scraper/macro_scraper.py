import requests
import asyncio
import asyncpg

def safe_float(val):
    if val is None:
        return None
    try:
        return float(val)
    except:
        return None

async def fetch_world_bank_data():
    print("Début de la collecte des indicateurs macro-économiques (World Bank)...")
    
    conn = await asyncpg.connect('postgresql://brvm_user:brvm_password@localhost:5433/brvm_tracker')
    
    try:
        pays_list = await conn.fetch('SELECT id, code, nom FROM pays WHERE code IS NOT NULL')
        
        indicators = {
            'croissance_pib': 'NY.GDP.MKTP.KD.ZG',
            'inflation': 'FP.CPI.TOTL.ZG',
            'population': 'SP.POP.TOTL'
        }
        
        for pays in pays_list:
            pays_id = pays['id']
            iso3 = pays['code'].upper()
            pays_nom = pays['nom']
            
            try:
                print(f" -> Récupération pour {pays_nom} ({iso3})...")
                macro_data = {}
                target_year = None
                
                for key, ind_code in indicators.items():
                    url = f'http://api.worldbank.org/v2/country/{iso3}/indicator/{ind_code}?format=json&per_page=3'
                    res = requests.get(url, timeout=10)
                    if res.status_code == 200:
                        data = res.json()
                        if len(data) == 2 and isinstance(data[1], list):
                            for row in data[1]:
                                if row['value'] is not None:
                                    macro_data[key] = row['value']
                                    if target_year is None:
                                        target_year = int(row['date'])
                                    break
                
                if target_year and macro_data:
                    # Vérifier si on l'a déjà
                    exist = await conn.fetchrow('SELECT id FROM indicateurs_macro WHERE pays_id = $1 AND annee = $2', pays_id, target_year)
                    
                    c_pib = safe_float(macro_data.get('croissance_pib'))
                    infl = safe_float(macro_data.get('inflation'))
                    pop = int(macro_data.get('population')) if 'population' in macro_data else None
                    
                    if exist:
                        await conn.execute('''
                            UPDATE indicateurs_macro 
                            SET croissance_pib = COALESCE($1, croissance_pib),
                                inflation = COALESCE($2, inflation),
                                population = COALESCE($3, population)
                            WHERE id = $4
                        ''', c_pib, infl, pop, exist['id'])
                    else:
                        await conn.execute('''
                            INSERT INTO indicateurs_macro (pays_id, annee, croissance_pib, inflation, population)
                            VALUES ($1, $2, $3, $4, $5)
                        ''', pays_id, target_year, c_pib, infl, pop)
                        
            except Exception as e:
                print(f"Erreur pour {pays_nom}: {e}")
                
        print("Fin de la collecte macro-économique.")
        
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(fetch_world_bank_data())
