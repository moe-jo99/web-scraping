import random
from playwright.async_api import async_playwright
import config
import asyncio

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
