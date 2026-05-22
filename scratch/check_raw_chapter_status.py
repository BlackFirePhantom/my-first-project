with open("scratch/raw_chapter.html", "r", encoding="utf-8") as f:
    html = f.read()

print("Length of raw HTML:", len(html))

# Let's count paragraphs and see if there is any error message
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, "lxml")
content_div = soup.select_one("div#mlfy_main_text")
if content_div:
    print("Found div#mlfy_main_text")
    txt = content_div.text[:500].encode('gbk', errors='replace').decode('gbk')
    print("Text in div#mlfy_main_text:")
    print(repr(txt))
    
    # Are there any scripts inside or around it?
    print("Children count:", len(list(content_div.children)))
    for i, child in enumerate(content_div.children):
        if child.name:
            t = child.text[:40].encode('gbk', errors='replace').decode('gbk')
            print(f"Child {i}: name={child.name}, text={repr(t)}")
else:
    print("div#mlfy_main_text NOT found in raw HTML")
