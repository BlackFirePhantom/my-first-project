import os
import sys
import time
from playwright.sync_api import sync_playwright

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

url = "https://www.linovelib.com/novel/8/1843.html"

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
    
    success = False
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt}/{max_retries}...")
            page.goto(url, timeout=20000, wait_until="domcontentloaded")
            page.wait_for_function(
                "() => { "
                "  const el = document.querySelector('div#mlfy_main_text'); "
                "  if (!el || !el.innerText) return false; "
                "  return !el.innerText.includes('正在加载') && !el.innerText.includes('内容加载失败'); "
                "}",
                timeout=15000
            )
            success = True
            break
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            time.sleep(2)
            
    if success:
        inner_text = page.evaluate("() => document.querySelector('#TextContent').innerText")
        print("Inner text length:", len(inner_text))
        
        # Save to file
        with open("scratch/page_innerText.txt", "w", encoding="utf-8") as f:
            f.write(inner_text)
        print("Saved innerText to scratch/page_innerText.txt")
    else:
        print("Failed to load page")
        
    page.close()
    browser.close()
