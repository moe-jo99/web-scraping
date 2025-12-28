import asyncio
import pandas as pd

async def get_business_links(page, search_query, location):
    url = f"https://www.yelp.ca/search?find_desc={search_query}&find_loc={location}"
    await page.goto(url)
    
    try:
        await page.wait_for_selector('div[class*="container"]', timeout=10000)
    except:
        print("Timeout or CAPTCHA detected")
        print("\a") # alert
        if "Captcha" in await page.title():
            input("Solve CAPTCHA and press enter")

    links = await page.evaluate('''() => {
        return Array.from(document.querySelectorAll('a[href^="/biz/"]'))
            .map(a => a.href)
            .filter(href => !href.includes("ad_business_id"))
            .filter((v, i, a) => a.indexOf(v) === i);
    }''')
    return links

async def extract_business_data(page, url):
    await page.goto(url)
    await page.wait_for_load_state('domcontentloaded')
    
    meta_content = await page.locator('meta[name="description"]').get_attribute('content')
    if not meta_content:
        return None

    parts = meta_content.split(', ')
    return {
        "Name": parts[0] if len(parts) > 0 else "N/A",
        "Address": parts[1] if len(parts) > 1 else "N/A",
        "Phone": parts[3] if len(parts) > 3 and any(char.isdigit() for char in parts[3]) else "N/A",
        "URL": url
    }

async def get_next_page_url(page):
    """
    Checks if a 'Next Page' button exists and returns the URL path if found
    """
    try:
        # Look for 'Next' button
        next_button = page.locator('a[aria-label="Next"]')
        if await next_button.is_visible():
            return await next_button.get_attribute('href')
    except Exception:
        pass
    return None

async def extract_links_from_page(page):
    """
    Extracts business links from the current search results page
    """
    return await page.evaluate('''() => {
        return Array.from(document.querySelectorAll('a[href^="/biz/"]'))
            .map(a => a.href)
            .filter(href => !href.includes("ad_business_id"))
            .filter((v, i, a) => a.indexOf(v) === i);
    }''')