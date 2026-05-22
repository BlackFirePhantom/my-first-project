import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def trace_chapter():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Referer": "https://www.linovelib.com/"
    }
    
    current_url = "https://www.linovelib.com/novel/1/2.html"
    base_chapter_id = "2"
    
    for i in range(1, 10):
        print(f"\nFetching page {i}: {current_url}")
        resp = requests.get(current_url, headers=headers, verify=False, timeout=15)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        
        # Print content preview
        content_div = soup.select_one("div#mlfy_main_text")
        if content_div:
            # remove some script tags if any
            for script in content_div.select("script"):
                script.decompose()
            text = content_div.get_text(strip=True)
            print("Preview:", text[:100])
        else:
            print("Content div not found!")
            
        # Find next page link
        next_link = None
        for a in soup.select("a"):
            text = a.get_text(strip=True)
            if "下一页" in text or "下一章" in text:
                next_link = a
                break
                
        if next_link:
            href = next_link.get("href", "")
            next_url = urljoin(current_url, href)
            print(f"Link text: '{next_link.get_text(strip=True)}', href: '{href}', full: '{next_url}'")
            
            # Check if next URL is still in the same chapter
            # Chapter pages are typically formatted as: 2_2.html, 2_3.html, etc.
            # Next chapter is typically 3.html
            basename = href.split("/")[-1].split(".")[0]  # e.g., "2_2" or "3"
            if "_" in basename:
                chap_id, page_idx = basename.split("_")
            else:
                chap_id = basename
                page_idx = "1"
                
            if chap_id == base_chapter_id:
                current_url = next_url
            else:
                print("Next link belongs to the next chapter! Stopping pagination.")
                break
        else:
            print("No next page/chapter link found! Stopping.")
            break

if __name__ == "__main__":
    trace_chapter()
