"""
检查各分页的 innerHTML 中是否本身就有重复段落
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from collections import Counter

urls = [
    "https://www.linovelib.com/novel/8/1843.html",
    "https://www.linovelib.com/novel/8/1843_2.html",
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

    all_page_paragraphs = []
    for url in urls:
        page = context.new_page()
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        page.wait_for_function(
            "() => { const el = document.querySelector('div#mlfy_main_text'); if (!el || !el.innerText) return false; return !el.innerText.includes('正在加载'); }",
            timeout=15000
        )
        
        data = page.evaluate("""
            () => {
                const container = document.querySelector('#TextContent');
                const innerHtml = container ? container.innerHTML : '';
                let nextPage = null;
                const links = document.querySelectorAll('.mlfy_page a');
                for (const a of links) {
                    const t = a.innerText.trim();
                    if (t.includes('下一页')) {
                        nextPage = a.href;
                        break;
                    }
                }
                return { innerHtml, nextPage };
            }
        """)
        
        inner_html = data["innerHtml"]
        soup = BeautifulSoup(inner_html, "lxml")
        ps = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
        
        # Check internal duplicates
        counter = Counter(ps)
        dups = {t: c for t, c in counter.items() if c > 1}
        print(f"\nURL: {url}")
        print(f"  段落数: {len(ps)}, 内部重复: {len(dups)}")
        if dups:
            print("  内部重复示例:")
            for t, c in list(dups.items())[:3]:
                print(f"    x{c}: {t[:50]}")
        
        print(f"  末尾5段:")
        for t in ps[-5:]:
            print(f"    {t[:60]}")
        
        print(f"  下一页: {data['nextPage']}")
        all_page_paragraphs.append(ps)
        page.close()
    
    # 检查跨页重叠
    if len(all_page_paragraphs) == 2:
        p1, p2 = all_page_paragraphs
        print("\n\n=== 跨页检查 ===")
        print(f"第1页末尾10段:")
        for t in p1[-10:]:
            print(f"  {t[:60]}")
        print(f"\n第2页开头10段:")
        for t in p2[:10]:
            print(f"  {t[:60]}")
        
        # 检查最大重叠窗口
        for size in range(20, 0, -1):
            if size <= len(p1) and size <= len(p2):
                if p1[-size:] == p2[:size]:
                    print(f"\n跨页重叠段数: {size}")
                    break
        else:
            print("\n无直接跨页重叠")
    
    browser.close()
