import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def test():
    print("Starting Playwright for debug...")
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
        
        url = "https://www.linovelib.com/novel/1/5.html"
        print(f"Navigating to: {url}")
        try:
            page.goto(url, timeout=30000)
            
            print("Page loaded. Waiting 10 seconds for decryption to happen naturally...")
            for i in range(10):
                time.sleep(1)
                soup = BeautifulSoup(page.content(), "lxml")
                el = soup.select_one("div#mlfy_main_text")
                if el:
                    text = el.get_text(strip=True)
                    print(f"Sec {i+1}: text length = {len(text)}")
                    if len(text) > 100:
                        print(f"  Ends with: {repr(text[-100:])}")
                else:
                    print(f"Sec {i+1}: div#mlfy_main_text not found!")
            
            # Save the final HTML
            with open("scratch/debug_chapter_5.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            print("Saved final HTML to scratch/debug_chapter_5.html")
            
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    test()
