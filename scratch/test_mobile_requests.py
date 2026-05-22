import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_mobile():
    # Mobile chapter URL
    url = "https://w.linovelib.com/novel/1/2.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
        "Referer": "https://w.linovelib.com/"
    }
    
    print(f"Fetching mobile URL: {url}")
    try:
        resp = requests.get(url, headers=headers, verify=False, timeout=15)
        print("Status code:", resp.status_code)
        resp.encoding = "utf-8"
        
        soup = BeautifulSoup(resp.text, "lxml")
        print("Title:", soup.title.string if soup.title else "None")
        print("HTML length:", len(resp.text))
        
        content_div = soup.select_one("div#mlfy_main_text, div#readcontent, div.readcontent, div#chaptercontent")
        if not content_div:
            # Print some divs
            print("Common content containers not found. Found divs:")
            for div in soup.select("div")[:10]:
                print(f"  <{div.name} id='{div.get('id')}' class='{div.get('class')}'>")
        else:
            text = content_div.get_text(strip=True)
            print("Text length:", len(text))
            print("Preview:", text[:300])
            print("Ends with:", text[-100:])
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_mobile()
