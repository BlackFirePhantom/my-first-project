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
    
    # Print request headers for the main document
    def on_request(request):
        if request.url == url:
            print("Main document request headers:")
            for k, v in request.headers.items():
                print(f"  {k}: {v}")
                
    page.on("request", on_request)
    page.goto(url)
    browser.close()
