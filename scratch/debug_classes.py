import os
import sys
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
    page.goto(url, timeout=30000)
    
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
    
    # Inspect all stylesheet rules
    styles_info = page.evaluate("""() => {
        const rules = [];
        for (let i = 0; i < document.styleSheets.length; i++) {
            const sheet = document.styleSheets[i];
            try {
                const sheetRules = Array.from(sheet.cssRules || sheet.rules).map(r => r.cssText);
                rules.push({ index: i, ownerNode: sheet.ownerNode ? sheet.ownerNode.tagName : 'unknown', count: sheetRules.length, rules: sheetRules.slice(0, 10) });
            } catch (e) {
                rules.push({ index: i, error: e.message });
            }
        }
        return rules;
    }""")
    
    print("=== Stylesheets in page ===")
    for s in styles_info:
        print(s)
        
    # Inspect paragraphs in #TextContent
    p_info = page.evaluate("""() => {
        const ps = Array.from(document.querySelectorAll('#TextContent p'));
        return ps.map((p, idx) => {
            const style = window.getComputedStyle(p);
            return {
                idx,
                text: p.innerText.substring(0, 40),
                classes: Array.from(p.classList),
                display: style.display,
                visibility: style.visibility
            };
        });
    }""")
    
    print("\n=== First 30 paragraphs in DOM ===")
    for p in p_info[:30]:
        print(f"P {p['idx']:03d}: display={p['display']}, visibility={p['visibility']}, classes={p['classes']}, text={repr(p['text'])}")
        
    browser.close()
