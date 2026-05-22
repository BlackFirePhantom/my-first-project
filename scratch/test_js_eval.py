import time
from playwright.sync_api import sync_playwright

def test():
    print("Starting Playwright to debug JS eval...")
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
        
        url = "https://www.linovelib.com/novel/1/5.html"
        print(f"Navigating to: {url}")
        try:
            page.goto(url, timeout=30000)
            
            for i in range(15):
                time.sleep(1)
                
                # Check element existence
                el_exists = page.evaluate("() => !!document.querySelector('div#mlfy_main_text')")
                el_inner_text = page.evaluate("() => { const el = document.querySelector('div#mlfy_main_text'); return el ? el.innerText : null; }")
                
                condition_result = page.evaluate("""() => {
                    const el = document.querySelector('div#mlfy_main_text');
                    if (!el || !el.innerText) return 'no_element_or_text';
                    const text = el.innerText;
                    const c1 = !text.includes('內容加載失敗');
                    const c2 = !text.includes('内容加载失败');
                    const c3 = !text.includes('数据缺失');
                    const c4 = !text.includes('正在加载');
                    return {
                        result: c1 && c2 && c3 && c4,
                        c1, c2, c3, c4,
                        length: text.length,
                        preview: text.substring(0, 100)
                    };
                }""")
                
                print(f"Sec {i+1}:")
                print(f"  Element exists: {el_exists}")
                print(f"  Eval condition result: {condition_result}")
                
        except Exception as e:
            print("Error:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    test()
