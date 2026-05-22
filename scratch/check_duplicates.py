"""
检查 135 个段落中有多少重复，找出乱序根源
"""
import os
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
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
    time.sleep(2)
    
    # 获取所有 p 的详细信息
    paragraphs = page.evaluate("""
        () => {
            const container = document.querySelector('#TextContent');
            if (!container) return [];
            const allPs = Array.from(container.querySelectorAll('p'));
            return allPs.map((p, idx) => ({
                idx,
                text: p.innerText.trim().substring(0, 50),
                classes: p.className,
                outerHTML: p.outerHTML.substring(0, 80)
            }));
        }
    """)
    
    # 检查重复
    text_count = {}
    for item in paragraphs:
        t = item['text']
        if t:
            text_count[t] = text_count.get(t, 0) + 1
    
    duplicates = {t: c for t, c in text_count.items() if c > 1}
    print(f"总段落数: {len(paragraphs)}")
    print(f"重复文本数: {len(duplicates)}")
    if duplicates:
        print("\n重复段落示例:")
        for t, c in list(duplicates.items())[:5]:
            print(f"  x{c}: {t}")
    
    # 检查各 p 的 class 情况
    has_class_count = sum(1 for item in paragraphs if item['classes'].strip())
    no_class_count = sum(1 for item in paragraphs if not item['classes'].strip())
    print(f"\n有 class 的 p: {has_class_count}")
    print(f"无 class 的 p: {no_class_count}")
    
    # 打印前几个有 class 的 p
    with_class = [item for item in paragraphs if item['classes'].strip()][:10]
    print("\n有 class 的段落示例:")
    for item in with_class:
        print(f"  idx={item['idx']}, class='{item['classes']}', text={item['text']}")
    
    # 检查是否是分页导致的重复（网页可能包含上一页末尾的内容）
    print("\n=== 全部段落（显示索引和前50字）===")
    for item in paragraphs:
        marker = " [重复]" if text_count.get(item['text'], 0) > 1 else ""
        print(f"  {item['idx']:03d}: {item['text']}{marker}")
    
    page.close()
    browser.close()
