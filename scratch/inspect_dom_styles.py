import os
import sys
import time
from playwright.sync_api import sync_playwright

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
    
    success = False
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Attempt {attempt}/{max_retries}...")
            page.goto(url, timeout=20000, wait_until="domcontentloaded")
            
            # Wait for decryption
            page.wait_for_function(
                "() => { "
                "  const el = document.querySelector('div#mlfy_main_text'); "
                "  if (!el || !el.innerText) return false; "
                "  return !el.innerText.includes('正在加载') && !el.innerText.includes('内容加载失败'); "
                "}",
                timeout=15000
            )
            success = True
            break
        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")
            if attempt < max_retries:
                time.sleep(2)
                
    if success:
        # Let's inspect CSS and computed order of each paragraph
        result = page.evaluate("""() => {
            const container = document.querySelector('#TextContent');
            if (!container) return { error: "No #TextContent found" };
            
            const containerDisplay = window.getComputedStyle(container).display;
            
            const paragraphs = Array.from(container.querySelectorAll('p'));
            const pDetails = paragraphs.map((p, idx) => {
                const style = window.getComputedStyle(p);
                return {
                    index: idx,
                    text: p.innerText.substring(0, 30),
                    order: style.order,
                    position: style.position,
                    top: style.top,
                    display: style.display
                };
            });
            
            // Also check for style tags in document
            const styles = Array.from(document.querySelectorAll('style')).map(s => s.innerHTML);
            
            return {
                containerDisplay,
                pCount: paragraphs.length,
                pDetails: pDetails.slice(0, 40), // first 40 paragraphs
                styleCount: styles.length,
                styles: styles
            };
        }""")
        
        print("Container Display:", result.get("containerDisplay"))
        print("Paragraph Count:", result.get("pCount"))
        print("Style tag count:", result.get("styleCount"))
        
        print("\nFirst 40 paragraph details:")
        for detail in result.get("pDetails", []):
            # Print safely to avoid encoding errors
            txt = detail['text'].encode('gbk', errors='replace').decode('gbk')
            print(f"Index {detail['index']:02d}: order={detail['order']}, text={repr(txt)}")
            
        print("\nStyles:")
        for i, style_content in enumerate(result.get("styles", [])):
            print(f"Style tag {i}: len={len(style_content)}")
            if "order" in style_content or "TextContent" in style_content:
                print(style_content[:500])
    else:
        print("Failed to load page after retries.")
            
    page.close()
    browser.close()
