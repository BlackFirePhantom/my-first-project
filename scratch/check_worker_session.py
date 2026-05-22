"""
在 worker 相同的 session 环境中检查 #TextContent innerHTML
"""
import io, sys, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from collections import Counter

url = "https://www.linovelib.com/novel/8/1843.html"

with sync_playwright() as p:
    # 模拟 worker 的完全相同环境
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
    context.add_init_script(
        'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    )
    
    page = context.new_page()
    # 完全相同的 goto（不限 wait_until）
    page.goto(url, timeout=30000)
    
    # 完全相同的等待条件
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
    
    # 用 chapter 模式获取数据
    data = page.evaluate("""
        () => {
            const container = document.querySelector('#TextContent');
            const innerHtml = container ? container.innerHTML : '';
            let nextPage = null;
            const links = document.querySelectorAll('.mlfy_page a');
            for (const a of links) {
                const t = a.innerText.trim();
                if (t.includes('下一页') || t.includes('下一章')) {
                    nextPage = a.href;
                    break;
                }
            }
            return { innerHtml, nextPage };
        }
    """)
    
    inner_html = data["innerHtml"]
    soup = BeautifulSoup(inner_html, "lxml")
    ps = [p_tag.get_text(strip=True) for p_tag in soup.find_all("p") if p_tag.get_text(strip=True)]
    counter = Counter(ps)
    dups = {t: c for t, c in counter.items() if c > 1}
    
    print(f"段落数: {len(ps)}")
    print(f"内部重复: {len(dups)}")
    if dups:
        print("重复列表:")
        for text, count in dups.items():
            positions = [i for i, l in enumerate(ps) if l == text]
            print(f"  x{count} pos={positions}: {text[:50]}")
    else:
        print("✓ 无内部重复！")
    
    print(f"\n前20段:")
    for i, t in enumerate(ps[:20]):
        marker = " [重复]" if counter[t] > 1 else ""
        print(f"  {i:03d}: {t[:60]}{marker}")
    
    page.close()
    browser.close()
