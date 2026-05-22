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
    
    html = page.content()
    soup = BeautifulSoup(html, "lxml")
    content_div = soup.select_one("div#mlfy_main_text")
    
    # Print the exact string of the first 30 tags
    p_tags = content_div.find_all(recursive=False) # Direct children of content_div
    print(f"Total direct children: {len(p_tags)}")
    
    lines = []
    for i, child in enumerate(p_tags[:40]):
        lines.append(f"Child {i:02d}: tag={child.name}, html={str(child)}")
        
    page.close()
    browser.close()

with open("scratch/raw_p_tags.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Saved raw tag html to scratch/raw_p_tags.txt")
