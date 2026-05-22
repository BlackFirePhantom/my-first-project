import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def test():
    print("Starting headless Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        url = "https://www.linovelib.com/novel/1/2.html"
        print(f"Visiting chapter: {url}")
        try:
            page.goto(url, timeout=30000)
            
            # Wait for content to load
            time.sleep(3)
            
            html = page.content()
            print("HTML length:", len(html))
            
            soup = BeautifulSoup(html, "lxml")
            content_div = soup.select_one("div#mlfy_main_text")
            if content_div:
                text = content_div.get_text(strip=True)
                print("Text length:", len(text))
                print("Ends with:", text[-100:])
            else:
                print("Content div not found!")
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    test()
