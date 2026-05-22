import requests
from bs4 import BeautifulSoup
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_meta():
    url = "https://www.linovelib.com/novel/1.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Referer": "https://www.linovelib.com/"
    }
    
    print(f"Fetching: {url}")
    resp = requests.get(url, headers=headers, verify=False, timeout=15)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")
    
    # Extract book name
    # 1. <h1 class="book-name">
    # 2. <h1 id="name">
    # 3. meta tag
    name_tag = soup.select_one("h1.book-name, h1#name, div.book-info h1, h1")
    name = name_tag.get_text(strip=True) if name_tag else "未知"
    
    # Extract author
    # In parse_novel.py, we saw: <div class="book-author"> or similar.
    # Let's inspect the page content for author info.
    author = "未知"
    author_tag = soup.select_one("div.book-author, a.writer, .author, meta[property='og:novel:author']")
    if author_tag:
        if author_tag.name == "meta":
            author = author_tag.get("content", "未知")
        else:
            author = author_tag.get_text(strip=True)
            
    # Sometimes it has text like "作者：石踏一荣" or similar. Clean it up.
    author = re.sub(r"^作者[：:]\s*", "", author)
    
    # Also extract cover
    cover = ""
    cover_tag = soup.select_one("div.book-img img, img.book-cover, meta[property='og:image']")
    if cover_tag:
        if cover_tag.name == "meta":
            cover = cover_tag.get("content", "")
        else:
            cover = cover_tag.get("src", "") or cover_tag.get("data-src", "")
            
    print("Name:", name)
    print("Author:", author)
    print("Cover:", cover)

if __name__ == "__main__":
    test_meta()
