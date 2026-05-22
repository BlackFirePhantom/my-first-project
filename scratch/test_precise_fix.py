"""
精确验证：等待混淆 JS 执行后，检查 CSS insertRule 是否生效
及正确读取可见段落
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
    
    # 等待正文出现
    page.wait_for_function(
        "() => { "
        "  const el = document.querySelector('div#mlfy_main_text'); "
        "  if (!el || !el.innerText) return false; "
        "  const text = el.innerText; "
        "  return !text.includes('正在加载') && !text.includes('内容加载失败'); "
        "}",
        timeout=15000
    )
    
    # 额外等待确保混淆 JS 完全执行（包括 insertRule）
    import time
    time.sleep(2)
    
    # 详细检查 CSS 规则
    style_info = page.evaluate("""
        () => {
            const container = document.querySelector('#TextContent');
            if (!container) return { error: 'no container' };
            
            const allPs = Array.from(container.querySelectorAll('p'));
            let visibleCount = 0;
            let hiddenCount = 0;
            let visibleTexts = [];
            let hiddenClasses = [];
            
            allPs.forEach((p, idx) => {
                const style = window.getComputedStyle(p);
                if (style.display === 'none') {
                    hiddenCount++;
                    hiddenClasses.push({ idx, cls: p.className });
                } else {
                    visibleCount++;
                    if (visibleTexts.length < 5) {
                        visibleTexts.push(p.innerText.substring(0, 30));
                    }
                }
            });
            
            // 检查 style sheet 中的规则数量
            let styleRuleCount = 0;
            let styleRuleText = '';
            for (let i = 0; i < document.styleSheets.length; i++) {
                const sheet = document.styleSheets[i];
                try {
                    const rules = sheet.cssRules || sheet.rules;
                    if (!rules) continue;
                    for (let j = 0; j < rules.length; j++) {
                        const rule = rules[j];
                        if (rule.cssText && rule.cssText.includes('display: none') && 
                            rule.selectorText && rule.selectorText.includes('TextContent')) {
                            styleRuleCount++;
                            if (!styleRuleText) styleRuleText = rule.cssText.substring(0, 100);
                        }
                    }
                } catch(e) {}
            }
            
            return {
                totalP: allPs.length,
                visibleCount,
                hiddenCount,
                visibleTexts,
                hiddenClasses: hiddenClasses.slice(0, 5),
                styleRuleCount,
                styleRuleText
            };
        }
    """)
    
    print(f"总 p 标签数: {style_info['totalP']}")
    print(f"可见 p 标签数: {style_info['visibleCount']}")
    print(f"隐藏 p 标签数: {style_info['hiddenCount']}")
    print(f"CSS 中 display:none 规则数: {style_info['styleRuleCount']}")
    print(f"规则示例: {style_info.get('styleRuleText', 'N/A')}")
    print(f"\n前5个可见段落:")
    for t in style_info.get('visibleTexts', []):
        print(f"  {t}")
    print(f"\n前5个隐藏段落(idx, class):")
    for h in style_info.get('hiddenClasses', []):
        print(f"  idx={h['idx']}, class={h['cls']}")
    
    # 只提取可见段落的文字
    visible_paragraphs = page.evaluate("""
        () => {
            const container = document.querySelector('#TextContent');
            if (!container) return [];
            const allPs = Array.from(container.querySelectorAll('p'));
            const texts = [];
            allPs.forEach(p => {
                const style = window.getComputedStyle(p);
                if (style.display !== 'none') {
                    const text = p.innerText.trim();
                    if (text) texts.push(text);
                }
            });
            return texts;
        }
    """)
    
    print(f"\n过滤后可见段落数: {len(visible_paragraphs)}")
    print("前10段:")
    for i, t in enumerate(visible_paragraphs[:10]):
        print(f"  {i+1:02d}: {t}")
    print("...")
    print("后5段:")
    for i, t in enumerate(visible_paragraphs[-5:]):
        print(f"  {len(visible_paragraphs)-5+i+1:02d}: {t}")
    
    page.close()
    browser.close()
