import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def test():
    print("Starting Playwright (headless=False, offscreen)...")
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
            viewport={"width": 800, "height": 600}
        )
        page = context.new_page()
        
        url = "https://www.linovelib.com/novel/1/2.html"
        print(f"Navigating to: {url}")
        
        start_time = time.time()
        page.goto(url, timeout=30000)
        
        print("Page navigated. Waiting for condition...")
        # Wait for div#mlfy_main_text to have > 800 characters
        try:
            page.wait_for_function(
                "() => { "
                "  const el = document.querySelector('div#mlfy_main_text'); "
                "  if (!el || !el.innerText) return false; "
                "  const text = el.innerText; "
                "  return !text.includes('內容加載失敗') && "
                "         !text.includes('内容加载失败') && "
                "         !text.includes('数据缺失') && "
                "         !text.includes('正在加载'); "
                "}",
                timeout=10000
            )
            print(f"Condition met in {time.time() - start_time:.2f} seconds!")
        except Exception as e:
            print("Wait failed/timed out:", e)
            
        html = page.content()
        soup = BeautifulSoup(html, "lxml")
        content_div = soup.select_one("div#mlfy_main_text")
        if content_div:
            text = content_div.get_text(strip=True)
            print("Text length retrieved:", len(text))
            print("Preview of last 100 chars:", text[-100:])
        else:
            print("Content div not found!")
            
        browser.close()

if __name__ == "__main__":
    test()
