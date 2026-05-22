import requests
from bs4 import BeautifulSoup

def test():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Referer": "https://www.linovelib.com/"
    }
    
    urls = [
        "https://www.linovelib.com/novel/1.html",
        "https://www.linovelib.com/novel/1/catalog",
        "https://www.linovelib.com/novel/1/2.html"
    ]
    
    session = requests.Session()
    
    for url in urls:
        print(f"\n--- Testing with verify=True: {url} ---")
        try:
            resp = session.get(url, headers=headers, timeout=15, verify=True)
            print("Status code:", resp.status_code)
            resp.encoding = "utf-8"
            if "Just a moment" in resp.text[:1000] or "验证" in resp.text[:1000]:
                print("CF Blocked!")
            else:
                soup = BeautifulSoup(resp.text, "lxml")
                print("Title:", soup.title.string if soup.title else "None")
                print("HTML len:", len(resp.text))
        except Exception as e:
            print("Error:", e)
            
    for url in urls:
        print(f"\n--- Testing with verify=False: {url} ---")
        try:
            resp = session.get(url, headers=headers, timeout=15, verify=False)
            print("Status code:", resp.status_code)
            resp.encoding = "utf-8"
            if "Just a moment" in resp.text[:1000] or "验证" in resp.text[:1000]:
                print("CF Blocked!")
            else:
                soup = BeautifulSoup(resp.text, "lxml")
                print("Title:", soup.title.string if soup.title else "None")
                print("HTML len:", len(resp.text))
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    test()
