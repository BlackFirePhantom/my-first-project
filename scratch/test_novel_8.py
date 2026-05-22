import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from novel_sources import linovelib, cache

# Clear cache to get fresh live behavior
cache.clear_all()

novel_url = "https://www.linovelib.com/novel/8.html"
print("Fetching chapters for novel 8...")
chapters = linovelib.get_chapters(novel_url, force_refresh=True)
print(f"Total chapters: {len(chapters)}")

for i in range(min(10, len(chapters))):
    print(f"Index {i}: {chapters[i]['title']} -> {chapters[i]['url']}")
