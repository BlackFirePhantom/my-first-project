import os
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
    )
    page = context.new_page()
    
    # Listen to network requests
    requests_log = []
    page.on("request", lambda request: requests_log.append(f"Request: {request.method} {request.url}"))
    page.on("response", lambda response: requests_log.append(f"Response: {response.status} {response.url}"))
    
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
    
    # Dump log
    with open("scratch/network_log.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(requests_log))
    print("Saved network log to scratch/network_log.txt")
    
    browser.close()
