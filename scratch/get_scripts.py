import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": "https://www.linovelib.com",
}

urls = [
    "https://www.linovelib.com/themes/zhpc/js/pctheme.js",
    "https://www.linovelib.com/scripts/chapterlog.js",
]

for url in urls:
    print(f"Fetching {url}")
    resp = requests.get(url, headers=headers)
    filename = url.split("/")[-1]
    with open(f"scratch/{filename}", "w", encoding="utf-8") as f:
        f.write(resp.text)
    print(f"Saved {filename}")
