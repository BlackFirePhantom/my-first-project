import os
import sys
import time
from playwright.sync_api import sync_playwright

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
    print("Navigating...")
    page.goto(url, timeout=30000)
    
    # Wait for decryption
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
    
    # Wait a bit more for rendering
    time.sleep(2)
    
    # Take screenshot of the text content area
    el = page.query_selector("div#mlfy_main_text")
    if el:
        el.screenshot(path="scratch/screenshot_content.png")
        print("Saved screenshot of div#mlfy_main_text to scratch/screenshot_content.png")
    else:
        page.screenshot(path="scratch/screenshot_page.png")
        print("Saved screenshot of whole page to scratch/screenshot_page.png")
        
    # Also dump the innerText
    inner_text = page.evaluate("() => document.querySelector('#TextContent').innerText")
    with open("scratch/screenshot_inner_text.txt", "w", encoding="utf-8") as f:
        f.write(inner_text)
    print("Saved innerText to scratch/screenshot_inner_text.txt")
    
    # Let's check style tags count again in this browser instance
    style_count = page.evaluate("() => document.querySelectorAll('style').length")
    print(f"Style tags in page: {style_count}")
    
    # Let's inspect style contents
    styles = page.evaluate("() => Array.from(document.querySelectorAll('style')).map(s => s.innerHTML)")
    for i, s in enumerate(styles):
        print(f"Style {i} (len={len(s)}): {s[:100]}...")
        if "display: none" in s:
            print("  Contains 'display: none'!")
            
    browser.close()
