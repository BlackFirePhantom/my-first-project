import re

# Read chapterlog.js
with open("scratch/chapterlog.js", "r", encoding="utf-8") as f:
    content = f.read()

# Let's find the obfuscated block
# It starts with (function(_0x or similar
match = re.search(r"\(function\(_0x.*", content)
if match:
    obfuscated_js = match.group(0)
    print(f"Found obfuscated JS of length: {len(obfuscated_js)}")
    
    # Save the obfuscated JS to a separate file for inspection
    with open("scratch/obfuscated_block.js", "w", encoding="utf-8") as out:
        out.write(obfuscated_js)
    print("Saved obfuscated block to scratch/obfuscated_block.js")
    
    # Let's search for keywords in the raw obfuscated text
    keywords = ["TextContent", "display", "order", "sort", "class", "style", "insertBefore", "clone", "paragraph"]
    for kw in keywords:
        found = kw in obfuscated_js
        print(f"Keyword '{kw}' in obfuscated JS: {found}")
else:
    print("No obfuscated block found matching pattern.")
