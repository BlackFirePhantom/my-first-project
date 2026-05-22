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
    
    # 1. Print all <style> tags in the whole page, especially near div#mlfy_main_text
    style_tags = soup.find_all("style")
    print(f"Total <style> tags found: {len(style_tags)}")
    for i, st in enumerate(style_tags):
        print(f"Style {i}: text length={len(st.text)}")
        if "TextContent" in st.text or "mlfy" in st.text or "order" in st.text:
            print(f"--- MATCH IN STYLE {i} ---")
            print(st.text[:1000])
            print("------------------------")
            
    # 2. Check if there are stylesheets loaded
    link_tags = soup.find_all("link", rel="stylesheet")
    print(f"Total stylesheet links: {len(link_tags)}")
    for link in link_tags:
        print(f"Link: {link.get('href')}")
        
    page.close()
    browser.close()
