import sys
import os
from bs4 import BeautifulSoup

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

def parse_chapter():
    with open("chapter_2.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "lxml")
    
    print("Title:", soup.title.string if soup.title else "None")
    
    # Let's search for content containers.
    # Usually in linovelib, the main text container has an id like `acontent`, `readcontent`, `content`, `mlfy_main_text` etc.
    # Let's print out all divs with IDs or classes containing 'content' or 'text' or 'read'
    print("\nContainers containing content/text/read in ID/class:")
    for div in soup.select("div"):
        div_id = div.get("id", "")
        div_class = div.get("class", [])
        if any(x in str(div_id) or any(x in str(c) for c in div_class) for x in ["content", "text", "read"]):
            text_preview = div.get_text(strip=True)[:100]
            if text_preview:
                print(f"  <{div.name} id='{div_id}' class='{div_class}'>: {text_preview}")
                
    # In linovelib, is there a "next page" button? Some sites split a chapter into multiple pages (e.g. page 1, page 2).
    # Let's inspect the page buttons
    print("\nNext page / navigation links:")
    for a in soup.select("a"):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        if "下一" in text or "下一页" in text or "下一章" in text:
            print(f"  {text} -> {href}")

if __name__ == "__main__":
    parse_chapter()
