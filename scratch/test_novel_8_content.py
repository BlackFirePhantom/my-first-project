import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from novel_sources import linovelib, cache

# Clear cache to get fresh live behavior
cache.clear_all()

url = "https://www.linovelib.com/novel/8/1843.html"
print(f"Fetching content for URL: {url}...")
try:
    content = linovelib.get_content(url)
    # Save the output to a text file for manual inspection first
    out_file = "scratch/novel_8_content_1843.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Full content saved to {out_file}")
    
    print("SUCCESS!")
    print(f"Content length: {len(content)}")
    print("Content preview (first 500 chars):")
    print(content[:500].encode('gbk', errors='replace').decode('gbk'))
    print("\nContent preview (last 500 chars):")
    print(content[-500:].encode('gbk', errors='replace').decode('gbk'))
except Exception as e:
    print("FAILED:", e)
