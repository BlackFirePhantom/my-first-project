import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def test():
    print("Starting Playwright for mobile domains...")
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
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
            viewport={"width": 375, "height": 812},
            is_mobile=True,
            has_touch=True
        )
        context.add_init_script(
            'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        )
        
        page = context.new_page()
        
        try:
            # 1. Try w.linovelib.com
            url_w_linovelib = "https://w.linovelib.com/search.html?searchkey=%E6%97%A0%E8%81%8C%E8%BD%AC%E7%94%9F"
            print(f"Visiting mobile search page: {url_w_linovelib}")
            page.goto(url_w_linovelib, timeout=30000)
            
            print("Waiting 10 seconds for mobile search page...")
            for i in range(10):
                time.sleep(1)
                print(f"Seconds waited: {i+1}, title: {page.title()}")
            
            html = page.content()
            print("HTML length:", len(html))
            
            # Let's save html
            with open("search_w_linovelib.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Saved search_w_linovelib.html")
            
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    test()
