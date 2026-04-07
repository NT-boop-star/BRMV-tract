import asyncio
from playwright.async_api import async_playwright

async def debug_news():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("https://www.richbourse.com/common/actualite/index", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        
        # Let's find any element containing '202' (for dates) or 'Sika' etc.
        # Or let's just get the HTML of the main content column.
        col = await page.query_selector(".col-md-9")
        if not col:
            col = await page.query_selector(".col-lg-9")
        if not col:
            col = await page.query_selector("body")
            
        html = await col.inner_html()
        
        # Write to file so we can view it nicely
        with open("richbourse_news_dom.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        await browser.close()
        
if __name__ == "__main__":
    asyncio.run(debug_news())
