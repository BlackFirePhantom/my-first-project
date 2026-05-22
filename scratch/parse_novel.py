import sys
import os
from bs4 import BeautifulSoup

def parse_novel():
    with open("novel_1.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "lxml")
    
    # Let's print the title and some headers to see the structure
    print("Page Title:", soup.title.string if soup.title else "None")
    
    # Try finding novel name and author
    # Usually in some h1, class, or meta tag
    # Let's print some likely elements
    print("\nLikely novel headers:")
    for h1 in soup.select("h1"):
        print("  h1:", h1.get_text(strip=True))
    for h2 in soup.select("h2"):
        print("  h2:", h2.get_text(strip=True))
        
    # Print elements with classes related to book details
    print("\nClasses with book/novel/author:")
    for div in soup.select("[class*='book'], [class*='novel'], [class*='author']"):
        # print first few characters or tag name
        print(f"  <{div.name} class='{div.get('class')}'>: {div.get_text(strip=True)[:100]}")
        
    # Check for catalog or chapter links
    print("\nLinks containing 'catalog' or 'index' or similar:")
    for a in soup.select("a"):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        if any(x in href or x in text for x in ["catalog", "目录", "read", "开始阅读", "chapter"]):
            print(f"  {text} -> {href}")

if __name__ == "__main__":
    parse_novel()
