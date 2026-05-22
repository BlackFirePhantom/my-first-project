import requests
from bs4 import BeautifulSoup

url = "https://www.linovelib.com/novel/8/1843.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": "https://www.linovelib.com",
}

print("Fetching via requests...")
resp = requests.get(url, headers=headers)
print("Status code:", resp.status_code)

soup = BeautifulSoup(resp.text, "lxml")
content_div = soup.select_one("div#TextContent")
if content_div:
    p_tags = content_div.select("p")
    print(f"Total P tags: {len(p_tags)}")
    for i, p in enumerate(p_tags[:15]):
        print(f"P {i:02d}: text={repr(p.get_text(strip=True))}")
else:
    print("No div#TextContent found in raw HTML!")
