import os
import json
import hashlib

url = 'https://www.linovelib.com/novel/1/2.html'
key = hashlib.md5(url.encode()).hexdigest()
path = f'cache/content/{key}.json'

print("Cache file path:", path)
if os.path.exists(path):
    print("Exists: True")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        val = data.get("value", "")
        print("Content length:", len(val))
        # Write to a clean text file
        out_path = "scratch/cached_content.txt"
        with open(out_path, "w", encoding="utf-8") as out_f:
            out_f.write(val)
        print("Written cache content to scratch/cached_content.txt")
        print("First 200 chars repr:", repr(val[:200]))
        print("Last 200 chars repr:", repr(val[-200:]))
    except Exception as e:
        print("Error reading cache file:", e)
else:
    print("Exists: False")
