import sys
import os
from bs4 import BeautifulSoup

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

def parse_catalog():
    with open("catalog_1.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "lxml")
    
    # Let's inspect the layout of chapters.
    # Where are the chapter links located?
    # Usually in <li class="chapter-li"> or <div class="chapter-div"> or similar.
    # Let's print the parent hierarchy of some chapter links.
    print("Chapter link parent analysis:")
    count = 0
    for a in soup.select("a"):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        # Match chapter link like /novel/1/2.html
        if "/novel/1/" in href and ".html" in href:
            parent = a.parent
            grandparent = parent.parent if parent else None
            print(f"Link: {text} -> {href}")
            print(f"  Parent: <{parent.name} class='{parent.get('class')}'>")
            if grandparent:
                print(f"  Grandparent: <{grandparent.name} class='{grandparent.get('class')}'>")
            count += 1
            if count >= 10:
                break

if __name__ == "__main__":
    parse_catalog()
