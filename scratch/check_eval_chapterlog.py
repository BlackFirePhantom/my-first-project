with open("scratch/chapterlog.js", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = list(re.finditer(r'eval', content, re.IGNORECASE))
print("Total matches:", len(matches))
for i, match in enumerate(matches):
    start = max(0, match.start() - 100)
    end = min(len(content), match.end() + 200)
    print(f"Match {i}:")
    print(content[start:end])
    print("-" * 50)
