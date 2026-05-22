"""
验证修复方案：用 page.evaluate 读取 #TextContent 的 innerText
这样浏览器渲染引擎已经应用了 CSS，隐藏的克隆段落不会出现在 innerText 中
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
    
    # 等待正文加载完毕
    page.wait_for_function(
        "() => { "
        "  const el = document.querySelector('div#mlfy_main_text'); "
        "  if (!el || !el.innerText) return false; "
        "  const text = el.innerText; "
        "  return !text.includes('正在加载') && !text.includes('内容加载失败'); "
        "}",
        timeout=15000
    )

    # 等待 JS 混淆执行完毕（克隆 p 插入 + CSS 动态生成）
    # DOMContentLoaded 已经触发，但 pctheme.js 中的代码也是在 DOMContentLoaded 里执行
    # 我们需要等待 style 标签被插入
    page.wait_for_function(
        "() => { "
        "  return document.head.querySelectorAll('style').length > 0; "
        "}",
        timeout=5000
    )
    
    print("JS 混淆执行完毕，读取 innerText...")
    
    # 方案A：用 innerText（只返回可见文字，display:none 的不包含）
    inner_text = page.evaluate("""
        () => {
            const container = document.querySelector('#TextContent');
            if (!container) return '';
            return container.innerText;
        }
    """)
    
    # 同时统计DOM中的 p 标签数量
    p_count = page.evaluate("""
        () => {
            const container = document.querySelector('#TextContent');
            return container ? container.querySelectorAll('p').length : 0;
        }
    """)
    
    # 统计可见的 p 标签数量
    visible_p_count = page.evaluate("""
        () => {
            const container = document.querySelector('#TextContent');
            if (!container) return 0;
            const ps = container.querySelectorAll('p');
            let count = 0;
            ps.forEach(p => {
                const style = window.getComputedStyle(p);
                if (style.display !== 'none') count++;
            });
            return count;
        }
    """)
    
    # 用 innerText 获取各行
    lines = [line.strip() for line in inner_text.split('\n') if line.strip()]
    
    print(f"DOM 中 p 标签总数: {p_count}")
    print(f"可见 p 标签数量: {visible_p_count}")
    print(f"innerText 非空行数: {len(lines)}")
    print()
    print("=== 前 20 行 innerText ===")
    for i, line in enumerate(lines[:20]):
        print(f"{i+1:02d}: {line}")
    
    print()
    print("=== 后 10 行 innerText ===")
    for i, line in enumerate(lines[-10:]):
        print(f"{len(lines)-10+i+1:02d}: {line}")
    
    # 保存完整 innerText
    with open("scratch/fixed_innerText.txt", "w", encoding="utf-8") as f:
        f.write(inner_text)
    print(f"\n完整 innerText 已保存到 scratch/fixed_innerText.txt ({len(inner_text)} 字符)")
    
    page.close()
    browser.close()
