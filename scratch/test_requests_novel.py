import requests
from bs4 import BeautifulSoup

def test():
    url = "https://www.linovelib.com/novel/1.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Referer": "https://www.linovelib.com/"
    }
    print(f"Requesting novel page via requests: {url}")
    try:
        resp = requests.get(url, headers=headers, timeout=15, verify=False)
        print("Status code:", resp.status_code)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        print("Title:", soup.title.string if soup.title else "None")
        if "Just a moment" in resp.text[:1000] or "验证" in resp.text[:1000] or "Perform" in resp.text[:1000]:
            print("Detected Cloudflare blockage!")
        else:
            print("Successfully bypassed Cloudflare with simple requests!")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test()
