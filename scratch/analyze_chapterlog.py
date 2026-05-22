with open("scratch/chapterlog.js", "r", encoding="utf-8") as f:
    content = f.read()

print("Length of chapterlog.js:", len(content))

# Look for typical script loading/fetching keywords
keywords = ["url", "http", "crypt", "decrypt", "cipher", "post", "get", "eval", "XMLHttpRequest", "fetch"]
for kw in keywords:
    count = content.lower().count(kw.lower())
    print(f"Keyword '{kw}': {count}")

# Print first 500 characters
print("\nFirst 500 chars:")
print(content[:500])

# Look for any matches of url or path
import re
urls = re.findall(r'https?://[^\s\'"]+|/[a-zA-Z0-9_/]+\.php|/[a-zA-Z0-9_/]+\.js', content)
print(f"\nURLs/paths found: {len(urls)}")
for u in set(urls)[:20]:
    print("  ", u)
