import asyncio
import asyncpg

import re

DB_CONFIG = {
    'host': 'localhost', 'port': 5433,
    'user': 'brvm_user', 'password': 'brvm_password',
    'database': 'brvm_tracker'
}

SPECIAL_MAPPING = {
    "BOA NG": "BOAN",
    "BOA CI": "BOAC",
    "BOA ML": "BOAM",
    "BOA SN": "BOAS",
    "BOA BF": "BOABF",
    "BOA BN": "BOAB",
    "SGCI": "SGBC",
    "SOGB": "SOGC",
}

async def relink():
    conn = await asyncpg.connect(**DB_CONFIG)
    
    actions = await conn.fetch('SELECT id, ticker, nom FROM actions')
    ticker_to_id = {a['ticker'].upper(): a['id'] for a in actions}
    
    keywords = []
    for a in actions:
        ticker = a['ticker'].upper()
        keywords.append((ticker, a['id']))
        for word in a['nom'].split():
            if len(word) >= 4:
                keywords.append((word.upper(), a['id']))
                
    for special_name, ticker in SPECIAL_MAPPING.items():
        if ticker in ticker_to_id:
            keywords.append((special_name.upper(), ticker_to_id[ticker]))
            
    # Add a fallback for names that match the start
    # e.g. SNTS for SONATEL
    if "SNTS" in ticker_to_id:
        keywords.append(("SONATEL", ticker_to_id["SNTS"]))
        keywords.append(("SNT", ticker_to_id["SNTS"]))
    
    def find_id(titre):
        t = titre.upper()
        
        # Try exact ticker matching first with word boundaries
        for kw, aid in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', t):
                return aid
                
        # Fallback to substring matching
        for kw, aid in keywords:
            if len(kw) >= 4 and kw in t:
                return aid
        return None
    
    news = await conn.fetch('SELECT id, titre FROM news WHERE action_id IS NULL')
    
    updated = 0
    for n in news:
        aid = find_id(n['titre'])
        if aid:
            await conn.execute('UPDATE news SET action_id = $1 WHERE id = $2', aid, n['id'])
            updated += 1
            print(f"Lien créé: '{n['titre']}' -> Action ID {aid}")
    
    total = await conn.fetchval('SELECT COUNT(*) FROM news WHERE action_id IS NOT NULL')
    print(f'News reliees a une action : {total} (dont {updated} nouvellement liees)')
    await conn.close()

asyncio.run(relink())
