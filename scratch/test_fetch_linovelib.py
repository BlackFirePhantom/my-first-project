import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import requests
from bs4 import BeautifulSoup
from novel_sources import robust_get

url = "https://www.linovelib.com/novel/3095/catalog"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": "https://www.linovelib.com",
}

print("Fetching via requests...")
try:
    resp = robust_get(url, headers=headers, timeout=15)
    print("Status code:", resp.status_code)
    print("Text preview:", resp.text[:500])
    
    soup = BeautifulSoup(resp.text, "lxml")
    title = soup.title.get_text() if soup.title else "No Title"
    print("Title:", title)
    volumes = soup.select(".volume-list > .volume")
    print("Volumes count:", len(volumes))
except Exception as e:
    print("Error:", e)
