"""Debug : sauvegarde la structure dans un fichier JSON."""
import sys, io, json
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import asyncio
from playwright.async_api import async_playwright

async def debug():
    result = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # --- VARIATIONS ---
        await page.goto("https://www.richbourse.com/common/variation/index", wait_until="networkidle")
        tables = await page.query_selector_all("table")
        
        var_info = {"nb_tables": len(tables), "headers": [], "sample_rows": []}
        if tables:
            rows = await tables[0].query_selector_all("tr")
            var_info["nb_rows"] = len(rows)
            
            if rows:
                ths = await rows[0].query_selector_all("th, td")
                var_info["headers"] = [await th.inner_text() for th in ths]
            
            for row in rows[1:4]:
                cells = await row.query_selector_all("td")
                vals = [await c.inner_text() for c in cells]
                var_info["sample_rows"].append({"nb_cols": len(cells), "values": vals})
        
        result["variations"] = var_info
        
        # --- DIVIDENDES ---
        await page.goto("https://www.richbourse.com/common/dividende/index", wait_until="networkidle")
        tables = await page.query_selector_all("table")
        
        div_info = {"nb_tables": len(tables), "headers": [], "sample_rows": []}
        if tables:
            rows = await tables[0].query_selector_all("tr")
            div_info["nb_rows"] = len(rows)
            
            if rows:
                ths = await rows[0].query_selector_all("th, td")
                div_info["headers"] = [await th.inner_text() for th in ths]
            
            for row in rows[1:4]:
                cells = await row.query_selector_all("td")
                vals = [await c.inner_text() for c in cells]
                div_info["sample_rows"].append({"nb_cols": len(cells), "values": vals})
        
        result["dividendes"] = div_info
        
        await browser.close()
    
    with open("debug_structure.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("Sauvegarde dans debug_structure.json")

asyncio.run(debug())
