import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def test():
    print("Starting Playwright for POST search via form submission...")
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
            # 1. Visit homepage
            url = "https://www.linovelib.com/"
            print(f"Visiting homepage: {url}")
            page.goto(url, timeout=30000)
            
            # Wait for page load
            time.sleep(3)
            print("Homepage title:", page.title())
            
            # 2. Fill search key and submit
            print("Filling search input and submitting form...")
            # Let's locate the searchkey input
            search_input = page.locator("input[name='searchkey']")
            search_input.fill("无职转生")
            
            # Press Enter to submit
            page.keyboard.press("Enter")
            
            # Wait for navigation / loading
            print("Waiting for search results page to load...")
            time.sleep(5)
            
            print("Search results page title:", page.title())
            
            # Let's see if we successfully bypassed Turnstile
            html = page.content()
            print("HTML length:", len(html))
            
            soup = BeautifulSoup(html, "lxml")
            
            # Save html
            with open("search_post_result.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Saved search_post_result.html")
            
            # Check what's in the page to find novel items
            links = []
            for a in soup.select("a"):
                href = a.get("href", "")
                text = a.get_text(strip=True)
                if href and text:
                    links.append((href, text))
            
            print("Found total links:", len(links))
            print("First 20 links:")
            for l in links[:20]:
                print(f"  {l[0]} -> {l[1]}")
                
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    test()
