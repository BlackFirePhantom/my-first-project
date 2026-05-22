with open("scratch/pctheme.js", "r", encoding="utf-8") as f:
    content = f.read()

import re
matches = list(re.finditer(r'eval', content, re.IGNORECASE))
print("Total eval matches in pctheme.js:", len(matches))
for i, match in enumerate(matches):
    print(f"Match {i} at {match.start()}: {content[match.start():match.start()+50]}...")
