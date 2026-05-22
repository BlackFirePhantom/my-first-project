from bs4 import BeautifulSoup

with open("scratch/pw_chapter.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")
content_div = soup.select_one("div#mlfy_main_text")
if content_div:
    p_tags = content_div.select("p")
    print(f"Total <p> tags in pw_chapter.html: {len(p_tags)}")
    for i, p in enumerate(p_tags[:15]):
        print(f"P {i:02d}: class={p.get('class')}, text={p.text[:40]}")
else:
    print("div#mlfy_main_text NOT found in pw_chapter.html")
