import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import browser_utils
import scraper
import config
import random

async def main():
    async with async_playwright() as p:
        browser, context = await browser_utils.get_browser_context(p)
        page = await context.new_page()
        
        search_query = config.DEFAULT_SEARCH
        location = config.DEFAULT_LOCATION
        
        all_business_links = []
        pages_to_scrape = 8 
        current_page = 1

        # search URL
        url = f"https://www.yelp.ca/search?find_desc={search_query}&find_loc={location}"

        while current_page <= pages_to_scrape:
            print(f"Scanning Search Page {current_page}...")
            await page.goto(url)
            await page.wait_for_timeout(20000)
            await browser_utils.human_scroll(page)
            await page.wait_for_timeout(3000)
            
            links = await scraper.extract_links_from_page(page)
            all_business_links.extend(links)
            
            # Go to Next page
            next_url_path = await scraper.get_next_page_url(page)
            if not next_url_path:
                print("No more pages found.")
                break
                
            url = f"https://www.yelp.ca{next_url_path}" if next_url_path.startswith('/') else next_url_path
            current_page += 1
            await asyncio.sleep(2)

        unique_links = list(set(all_business_links)) # remove duplicates
        print(f"Total unique businesses found: {len(unique_links)}")
        
        results = []
        for link in unique_links:
            print(f"Extracting details: {link}")
            data = await scraper.extract_business_data(page, link)
            if data:
                results.append(data)
            await asyncio.sleep(random.randint(2, 4)) 

        # export to Excel
        if results:
            pd.DataFrame(results).to_excel("yelp_results_multi_page.xlsx", index=False)
            print("Saved as yelp_results_multi_page.xlsx")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())