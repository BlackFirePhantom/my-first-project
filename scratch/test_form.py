import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def test():
    print("Starting Playwright for main page form analysis...")
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
            url = "https://www.linovelib.com/"
            print(f"Visiting main page: {url}")
            page.goto(url, timeout=30000)
            
            # Wait for main page to load
            time.sleep(3)
            
            html = page.content()
            soup = BeautifulSoup(html, "lxml")
            
            # Search for form tag
            print("\nForm tags found on main page:")
            for form in soup.select("form"):
                print(f"  Form action: {form.get('action')}, method: {form.get('method')}")
                for inp in form.select("input"):
                    print(f"    Input: name={inp.get('name')}, type={inp.get('type')}, value={inp.get('value')}")
            
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    test()
