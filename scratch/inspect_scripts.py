import os
import sys
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

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
    page.goto(url, timeout=20000, wait_until="domcontentloaded")
    
    # Wait for decryption
    page.wait_for_function(
        "() => { "
        "  const el = document.querySelector('div#mlfy_main_text'); "
        "  if (!el || !el.innerText) return false; "
        "  return !el.innerText.includes('正在加载'); "
        "}",
        timeout=15000
    )
    
    html = page.content()
    soup = BeautifulSoup(html, "lxml")
    
    # Let's inspect all script tags
    script_tags = soup.find_all("script")
    print(f"Total <script> tags: {len(script_tags)}")
    for i, s in enumerate(script_tags):
        src = s.get("src", "")
        text = s.text.strip()
        print(f"Script {i}: src={src}, text_len={len(text)}")
        if not src and len(text) > 0:
            print(f"  First 200 chars of inline script: {text[:200]}")
            
    page.close()
    browser.close()
