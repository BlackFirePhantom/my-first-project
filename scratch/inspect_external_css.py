import requests

url = "https://www.linovelib.com/themes/zhpc/css/chapter.css?v1126b2"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
}

try:
    resp = requests.get(url, headers=headers, timeout=10)
    print("CSS fetch status:", resp.status_code)
    css_content = resp.text
    print("CSS length:", len(css_content))
    
    # Check for order, flex, grid, TextContent, etc.
    with open("scratch/chapter.css", "w", encoding="utf-8") as f:
        f.write(css_content)
    print("Saved CSS to scratch/chapter.css")
    
    # Search for keywords
    for line in css_content.split("\n"):
        if "order" in line or "flex" in line or "TextContent" in line or "mlfy" in line:
            print("Match line:", line[:150])
except Exception as e:
    print("Error:", e)
