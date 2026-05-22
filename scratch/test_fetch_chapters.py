import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from novel_sources import linovelib, cache

# Clear cache first to ensure we test live behavior
cache.clear_all()

urls = [
    "https://www.linovelib.com/novel/1/3.html",   # Chapter 3
    "https://www.linovelib.com/novel/1/4.html",   # Chapter 4
    "https://www.linovelib.com/novel/1/5.html",   # Chapter 5
    "https://www.linovelib.com/novel/22/2070.html", # A different novel
]

for url in urls:
    print(f"\nFetching: {url}")
    try:
        content = linovelib.get_content(url)
        print("Success! Length:", len(content))
        print("First 150 chars:", repr(content[:150]))
        print("Last 150 chars:", repr(content[-150:]))
        if "内容加载失败" in content or "（內容加載失敗！請刷新或更換瀏覽器）" in content or "数据缺失" in content:
            print("WARNING: Contains error/placeholder text!")
        else:
            print("OK - No placeholders found.")
    except Exception as e:
        print("Failed:", e)
