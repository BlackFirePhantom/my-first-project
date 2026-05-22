import os
import sys
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

urls = [
    "https://www.linovelib.com/novel/8/1843.html",
    "https://www.linovelib.com/novel/8/1843_2.html",
    "https://www.linovelib.com/novel/8/1843_3.html",
    "https://www.linovelib.com/novel/8/1843_4.html",
    "https://www.linovelib.com/novel/8/1843_5.html",
]

output_lines = []

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
    
    for url in urls:
        output_lines.append(f"\n======================================")
        output_lines.append(f"URL: {url}")
        page = context.new_page()
        try:
            page.goto(url, timeout=20000, wait_until="domcontentloaded")
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
            html = page.content()
            soup = BeautifulSoup(html, "lxml")
            content_div = soup.select_one("div#mlfy_main_text")
            if content_div:
                p_tags = content_div.select("p")
                output_lines.append(f"Total <p> tags: {len(p_tags)}")
                for i, p_tag in enumerate(p_tags):
                    output_lines.append(f"  P {i:03d}: {p_tag.text.strip()}")
            else:
                output_lines.append("No div#mlfy_main_text found")
        except Exception as e:
            output_lines.append(f"Error fetching: {e}")
        finally:
            page.close()
            
    browser.close()

with open("scratch/pages_paragraphs.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))
print("Saved all pages' paragraphs to scratch/pages_paragraphs.txt")
