import os
import sys
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

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
    
    # Dump all inline script contents
    scripts = []
    for i, s in enumerate(soup.find_all("script")):
        src = s.get("src", "")
        text = s.text.strip()
        scripts.append(f"=== Script {i} (src={src}) ===")
        scripts.append(text)
        scripts.append("\n")
        
    with open("scratch/all_scripts.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(scripts))
    print("Saved all scripts to scratch/all_scripts.txt")
    
    browser.close()
