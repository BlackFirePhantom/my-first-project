import os
import sys
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
    
    # Track response sizes
    responses = []
    page.on("response", lambda response: responses.append((response.url, response.status, len(response.body()) if response.ok else 0)))
    
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
    with open("scratch/pw_chapter.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    print("Playwright HTML page.content() size:", len(html))
    
    print("\nResponses fetched:")
    for r_url, r_status, r_len in responses:
        if "1843.html" in r_url:
            print(f"  {r_url}: status={r_status}, size={r_len}")
            
    browser.close()
