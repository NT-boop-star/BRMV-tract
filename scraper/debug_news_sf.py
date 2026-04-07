import asyncio
from playwright.async_api import async_playwright

async def test_sf_news():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.sikafinance.com/marches/actualites", wait_until="networkidle")

        articles = await page.query_selector_all("a")
        for article in articles:
            text = await article.inner_text()
            href = await article.get_attribute("href")
            if href and 'actualites/' in href:
                print("SF Link:", href, "Text:", text.strip().replace('\n', ' | '))
        
        await browser.close()

asyncio.run(test_sf_news())
