import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

url = "https://www.linovelib.com/novel/22/2070.html"
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
    page = context.new_page()
    try:
        print(f"Visiting: {url}")
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        print("Page loaded. Waiting 10 seconds for any dynamic JS to execute...")
        time.sleep(10)
        
        html = page.content()
        with open("scratch/fail_2070.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Saved HTML to scratch/fail_2070.html")
        
        soup = BeautifulSoup(html, "lxml")
        el = soup.select_one("div#mlfy_main_text")
        if el:
            print("div#mlfy_main_text exists!")
            text = el.get_text(strip=True)
            print("Text length:", len(text))
            print("Preview:", repr(text[:200]))
        else:
            print("div#mlfy_main_text NOT found!")
            
    except Exception as e:
        print("Error during execution:", e)
    finally:
        browser.close()
