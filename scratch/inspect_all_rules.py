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
    page.goto(url, timeout=20000, wait_until="domcontentloaded")
    
    # Wait for decryption
    page.wait_for_function(
        "() => { "
        "  const el = document.querySelector('div#mlfy_main_text'); "
        "  if (!el || !el.innerText) return false; "
        "  const text = el.innerText; "
        "  return !text.includes('內容加載失败') && "
        "         !text.includes('内容加载失败') && "
        "         !text.includes('数据缺失') && "
        "         !text.includes('正在加载'); "
        "}",
        timeout=15000
    )
    
    # Dump all style rules that target #TextContent or display: none
    rules_info = page.evaluate("""() => {
        const matchingRules = [];
        for (let i = 0; i < document.styleSheets.length; i++) {
            const sheet = document.styleSheets[i];
            try {
                const cssRules = sheet.cssRules || sheet.rules;
                if (!cssRules) continue;
                for (let j = 0; j < cssRules.length; j++) {
                    const rule = cssRules[j];
                    if (rule.cssText && (rule.cssText.includes('TextContent') || rule.cssText.includes('display: none'))) {
                        matchingRules.push({
                            sheetIndex: i,
                            ownerTagName: sheet.ownerNode ? sheet.ownerNode.tagName : 'unknown',
                            ruleText: rule.cssText
                        });
                    }
                }
            } catch (e) {
                // cross-origin stylesheet might throw
            }
        }
        return matchingRules;
    }""")
    
    print(f"Total matching rules: {len(rules_info)}")
    for i, r in enumerate(rules_info[:50]):
        print(f"Rule {i:02d} (Sheet {r['sheetIndex']}, {r['ownerTagName']}): {r['ruleText']}")
        
    page.close()
    browser.close()
