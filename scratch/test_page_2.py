import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def test():
    print("Starting Playwright for page 2...")
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
            # Visit page 2 of chapter 2
            url = "https://www.linovelib.com/novel/1/2_2.html"
            print(f"Visiting page 2: {url}")
            page.goto(url, timeout=30000)
            
            # Wait a few seconds
            time.sleep(3)
            
            html = page.content()
            print("HTML length:", len(html))
            
            soup = BeautifulSoup(html, "lxml")
            print("Title:", soup.title.string)
            
            print("\nNext page / navigation links on page 2:")
            for a in soup.select("a"):
                href = a.get("href", "")
                text = a.get_text(strip=True)
                if "下" in text:
                    print(f"  {text} -> {href}")
            
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    test()
