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
        "  const text = el.innerText; "
        "  return !text.includes('內容加載失敗') && "
        "         !text.includes('内容加载失败') && "
        "         !text.includes('数据缺失') && "
        "         !text.includes('正在加载'); "
        "}",
        timeout=15000
    )
    
    # Let's inspect the paragraph tags and their attributes inside div#mlfy_main_text
    html = page.content()
    soup = BeautifulSoup(html, "lxml")
    content_div = soup.select_one("div#mlfy_main_text")
    
    print("=== Raw P Elements inside mlfy_main_text ===")
    p_tags = content_div.select("p")
    print(f"Total <p> tags: {len(p_tags)}")
    for i, p_tag in enumerate(p_tags[:15]):
        print(f"P {i}: tag={p_tag.name}, attrs={p_tag.attrs}, text={repr(p_tag.text[:60])}")
        
    page.close()
    browser.close()
