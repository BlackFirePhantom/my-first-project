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
    
    for url in urls:
        print(f"\nFetching URL: {url}")
        page = context.new_page()
        success = False
        max_retries = 3
        
        for attempt in range(1, max_retries + 1):
            try:
                print(f"  Attempt {attempt}/{max_retries}...")
                page.goto(url, timeout=20000, wait_until="domcontentloaded")
                
                print("  Waiting for decryption condition...")
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
                    timeout=15000
                )
                print("  Decryption condition met successfully!")
                
                html = page.content()
                soup = BeautifulSoup(html, "lxml")
                el = soup.select_one("div#mlfy_main_text")
                if el:
                    print(f"  Success! Text length: {len(el.get_text(strip=True))}")
                    success = True
                    break
            except Exception as e:
                print(f"  Attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    time.sleep(2)
                    
        if not success:
            print(f"  FAILED to load {url} after {max_retries} attempts.")
            
        page.close()
        
    browser.close()
