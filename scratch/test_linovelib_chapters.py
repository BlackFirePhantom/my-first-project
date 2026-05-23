import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from novel_sources import linovelib
import json

url = "https://www.linovelib.com/novel/3095.html"
print("Running get_chapters for:", url)
try:
    chapters = linovelib.get_chapters(url, force_refresh=True)
    print("Chapters count:", len(chapters))
    if chapters:
        print("First chapter:", chapters[0])
        print("Last chapter:", chapters[-1])
    else:
        print("No chapters returned!")
except Exception as e:
    print("Error:", e)
