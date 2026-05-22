import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from bs4 import BeautifulSoup
from novel_sources.dadehe import _fetch_page

def test_dadehe():
    print("Testing dadehe page fetch...")
    try:
        html = _fetch_page("https://www.dadehe.com/113167/")
        print("HTML length:", len(html))
        soup = BeautifulSoup(html, "lxml")
        print("Title:", soup.title.string if soup.title else "No title")
    except Exception as e:
        print("Error fetching dadehe:", e)

if __name__ == "__main__":
    test_dadehe()
