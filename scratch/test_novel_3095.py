import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.getcwd())

from novel_sources.linovelib import get_content, get_chapters
from novel_sources import cache

url = "https://www.linovelib.com/novel/3095.html"
chapters = get_chapters(url)
target_chapter = chapters[7]

print(f"Testing get_content for: {target_chapter['title']} -> {target_chapter['url']}")

# Clear cache
cache.set_content(target_chapter['url'], "")

content = get_content(target_chapter['url'])

# Save to file
with open("scratch/fetched_content_3095.txt", "w", encoding="utf-8") as f:
    f.write(content)

print(f"\nSuccess! Saved to scratch/fetched_content_3095.txt")
print(f"Total lines: {len(content.splitlines())}")

# Print first 5 and last 5 lines:
lines = content.splitlines()
print("\nFirst 5 lines:")
for idx, line in enumerate(lines[:5]):
    print(f"  {idx+1:02d}: {line}")
print("\nLast 5 lines:")
for idx, line in enumerate(lines[-5:]):
    print(f"  {len(lines)-5+idx+1:02d}: {line}")
