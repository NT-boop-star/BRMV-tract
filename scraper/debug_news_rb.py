import asyncio
from playwright.async_api import async_playwright

async def test_richbourse_news():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.richbourse.com/common/actualite/index", wait_until="networkidle")

        print("--- All Links ---")
        links = await page.query_selector_all("a[href*='/common/actualite/view']")
        for link in links[:5]:
            parent = await link.evaluate_handle('node => node.parentElement.parentElement')
            text = await parent.inner_text()
            print("Link:", await link.get_attribute("href"), "Text:", text.replace('\n', ' | '))
        
        await browser.close()

asyncio.run(test_richbourse_news())
