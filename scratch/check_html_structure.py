"""
检查 Playwright 渲染后的 HTML 中 TextContent 的原始 HTML 结构
"""
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
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
    page.goto(url, timeout=30000, wait_until="domcontentloaded")
    
    page.wait_for_function(
        "() => {"
        "  const el = document.querySelector('div#mlfy_main_text');"
        "  if (!el || !el.innerText) return false;"
        "  const text = el.innerText;"
        "  return !text.includes('正在加载') && !text.includes('内容加载失败');"
        "}",
        timeout=15000
    )
    
    import time
    time.sleep(1)  # 最短等待，不额外等
    
    # 获取 TextContent 的 innerHTML（不是整页）
    inner_html = page.evaluate("""
        () => {
            const container = document.querySelector('#TextContent');
            return container ? container.innerHTML : '';
        }
    """)
    
    soup = BeautifulSoup(inner_html, 'lxml')
    all_ps = soup.find_all('p')
    
    print(f"innerHTML 中 p 标签数量: {len(all_ps)}")
    
    # 统计 class 情况
    has_class = [p for p in all_ps if p.get('class')]
    no_class = [p for p in all_ps if not p.get('class')]
    print(f"有 class 的 p: {len(has_class)}")
    print(f"无 class 的 p: {len(no_class)}")
    
    # 检查重复
    texts = [p.get_text(strip=True) for p in all_ps]
    from collections import Counter
    text_counter = Counter(texts)
    duplicates = {t: c for t, c in text_counter.items() if c > 1}
    print(f"重复文本数: {len(duplicates)}")
    
    print("\n有 class 的 p 示例（这些是被混淆 JS 标记的）：")
    for p in has_class[:5]:
        print(f"  class={p.get('class')}, text={p.get_text(strip=True)[:40]}")
    
    print("\n前20个 p（显示顺序和 class）：")
    for i, p in enumerate(all_ps[:20]):
        cls = p.get('class', [])
        text = p.get_text(strip=True)[:40]
        dup = " [重复]" if text_counter.get(p.get_text(strip=True), 0) > 1 else ""
        print(f"  {i:03d}: cls={cls}, text={text}{dup}")
    
    page.close()
    browser.close()
