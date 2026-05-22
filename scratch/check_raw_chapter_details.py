with open("scratch/raw_chapter.html", "r", encoding="utf-8") as f:
    html = f.read()

print("Length of raw HTML:", len(html))

# Let's find mlfy_main_text in html
idx = html.find("mlfy_main_text")
if idx != -1:
    print("Found mlfy_main_text. Context:")
    # Print 2000 characters after it to see the structure
    print(html[idx-100:idx+2500])
else:
    print("mlfy_main_text not found in raw HTML")
