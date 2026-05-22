import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

urls = [
    "https://www.linovelib.com/novel/1/5_4.html",
    "https://www.linovelib.com/novel/22/2070.html",
]

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--window-position=-32000,-32000",
            "--window-size=10,10"
        ]
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        viewport={"width": 1024, "height": 768}
    )
    
    for idx, url in enumerate(urls):
        print(f"\nDebugging URL: {url}")
        page = context.new_page()
        try:
            page.goto(url, timeout=30000)
            time.sleep(5)  # Wait for any challenge or JS to run
            
            title = page.title()
            print("Page title:", title)
            
            html = page.content()
            soup = BeautifulSoup(html, "lxml")
            
            # Check for Cloudflare Turnstile
            cf_challenge = soup.select_one("#cf-challenge, #challenge-form, iframe[src*='challenges']")
            if cf_challenge:
                print("CLOUDFLARE TURNSTILE DETECTED!")
            
            el = soup.select_one("div#mlfy_main_text")
            if el:
                text = el.get_text(strip=True)
                print(f"div#mlfy_main_text exists! text length = {len(text)}")
                print(f"Preview (150 chars): {repr(text[:150])}")
            else:
                print("div#mlfy_main_text NOT found!")
                print(f"Body preview: {repr(soup.body.get_text(strip=True)[:300]) if soup.body else 'No body'}")
                
            with open(f"scratch/fail_{idx}.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"Saved HTML to scratch/fail_{idx}.html")
            
        except Exception as e:
            print("Error:", e)
        finally:
            page.close()
            
    browser.close()
