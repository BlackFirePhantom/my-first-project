"""
找出跨页重复的具体段落和其在各页中的位置
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from collections import Counter, defaultdict

urls = [
    "https://www.linovelib.com/novel/8/1843.html",
    "https://www.linovelib.com/novel/8/1843_2.html",
    "https://www.linovelib.com/novel/8/1843_3.html",
]

all_page_paragraphs = []

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
        page = context.new_page()
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        page.wait_for_function(
            "() => { const el = document.querySelector('div#mlfy_main_text'); return el && el.innerText && !el.innerText.includes('正在加载'); }",
            timeout=15000
        )
        
        data = page.evaluate("""
            () => {
                const container = document.querySelector('#TextContent');
                return container ? container.innerHTML : '';
            }
        """)
        
        soup = BeautifulSoup(data, "lxml")
        ps = [p_tag.get_text(strip=True) for p_tag in soup.find_all("p") if p_tag.get_text(strip=True)]
        all_page_paragraphs.append((url.split("/")[-1], ps))
        print(f"  页面 {url.split('/')[-1]}: {len(ps)} 段落")
        page.close()
    
    browser.close()

# 找出跨页重复
text_pages = defaultdict(list)
for page_name, ps in all_page_paragraphs:
    for i, text in enumerate(ps):
        text_pages[text].append((page_name, i))

cross_page_dups = {t: pages for t, pages in text_pages.items() if len(pages) > 1}
print(f"\n跨3页中出现重复的段落数: {len(cross_page_dups)}")

print("\n详细重复列表（前15个）：")
for text, pages in list(cross_page_dups.items())[:15]:
    print(f"\n  段落: {text[:60]}")
    for pg_name, idx in pages:
        print(f"    -> {pg_name} 第{idx}段")
