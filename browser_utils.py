import random
from playwright.async_api import async_playwright
import config
import asyncio
from fake_useragent import UserAgent

ua = UserAgent(browsers=['chrome', 'edge'])

async def get_browser_context(p):
    browser = await p.chromium.launch(
        headless=config.HEADLESS,
        channel=config.BROWSER_CHANNEL,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-extensions",
            "--use-gl=desktop",
            "--window-position=0,0"
        ]
    )
    context = await browser.new_context(
        user_agent=ua.random,
        viewport=config.VIEWPORT,
        locale=config.LOCALE,
        timezone_id=config.TIMEZONE
    )
    # stealth settings
    await context.add_init_script("""
        Object.defineProperty(navigator, 'languages', { get: () => ['en-CA', 'en'] });
        
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) return 'Intel Inc.';
            if (parameter === 37446) return 'Intel(R) Iris(TM) Graphics 6100';
            return getParameter.apply(this, arguments);
        };

        window.chrome = { runtime: {} };
    """)
    return browser, context

async def human_delay():
    await asyncio.sleep(random.randint(2, 5))

async def human_scroll(page):
    """Slowly scroll down the page to mimic a human reading."""
    for _ in range(random.randint(2, 4)):
        await page.mouse.wheel(0, random.randint(300, 600))
        await asyncio.sleep(random.uniform(0.5, 1.5))
