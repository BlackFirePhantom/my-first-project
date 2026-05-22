import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def test():
    print("Starting Playwright for catalog page...")
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
            viewport={"width": 1920, "height": 1080}
        )
        context.add_init_script(
            'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        )
        
        page = context.new_page()
        
        try:
            # Visit catalog page directly
            url = "https://www.linovelib.com/novel/1/catalog"
            print(f"Visiting catalog page: {url}")
            page.goto(url, timeout=30000)
            
            # Wait to see if Cloudflare Turnstile shows up
            for i in range(5):
                time.sleep(1)
                print(f"Seconds waited: {i+1}, title: {page.title()}")
            
            html = page.content()
            print("HTML length:", len(html))
            
            with open("catalog_1.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Saved catalog_1.html")
            
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    test()
