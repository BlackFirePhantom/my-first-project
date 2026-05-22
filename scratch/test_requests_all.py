import requests
from bs4 import BeautifulSoup

# Disable warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Referer": "https://www.linovelib.com/"
    }
    
    # 1. Test Catalog Page
    catalog_url = "https://www.linovelib.com/novel/1/catalog"
    print(f"Requesting catalog page: {catalog_url}")
    try:
        resp = requests.get(catalog_url, headers=headers, timeout=15, verify=False)
        print("Catalog Status code:", resp.status_code)
        resp.encoding = "utf-8"
        if "Just a moment" in resp.text[:1000] or "验证" in resp.text[:1000]:
            print("Catalog: Blocked by Cloudflare!")
        else:
            soup = BeautifulSoup(resp.text, "lxml")
            print("Catalog Title:", soup.title.string if soup.title else "None")
            print("Catalog HTML length:", len(resp.text))
    except Exception as e:
        print("Catalog Error:", e)

    # 2. Test Chapter Page
    chapter_url = "https://www.linovelib.com/novel/1/2.html"
    print(f"\nRequesting chapter page: {chapter_url}")
    try:
        resp = requests.get(chapter_url, headers=headers, timeout=15, verify=False)
        print("Chapter Status code:", resp.status_code)
        resp.encoding = "utf-8"
        if "Just a moment" in resp.text[:1000] or "验证" in resp.text[:1000]:
            print("Chapter: Blocked by Cloudflare!")
        else:
            soup = BeautifulSoup(resp.text, "lxml")
            print("Chapter Title:", soup.title.string if soup.title else "None")
            print("Chapter HTML length:", len(resp.text))
    except Exception as e:
        print("Chapter Error:", e)

if __name__ == "__main__":
    test()
