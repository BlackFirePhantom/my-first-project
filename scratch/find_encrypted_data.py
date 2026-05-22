import requests
from bs4 import BeautifulSoup

url = "https://www.linovelib.com/novel/8/1843.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": "https://www.linovelib.com",
}

resp = requests.get(url, headers=headers)
print("Status code:", resp.status_code)

# Let's save the raw HTML to a file so we can inspect it fully
with open("scratch/raw_chapter.html", "w", encoding="utf-8") as f:
    f.write(resp.text)
print("Saved raw HTML to scratch/raw_chapter.html")

# Search for potential variables or elements that hold the text
soup = BeautifulSoup(resp.text, "lxml")
for script in soup.find_all("script"):
    if script.text and len(script.text) > 1000:
        print(f"Large script tag found: len={len(script.text)}, preview={script.text[:100]}...")

# Search for any hidden input or elements
for tag in soup.find_all(attrs={"type": "hidden"}):
    print("Hidden input:", tag)

# Search for elements with a class that looks like content
for tag in soup.find_all(class_=lambda x: x and ('content' in x or 'text' in x)):
    print(f"Tag with class '{tag.get('class')}': id='{tag.get('id')}', tag='{tag.name}', children={len(list(tag.children))}")
