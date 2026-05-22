"""
验证修复后的 get_content() 是否能正确获取完整、有序的章节内容
"""
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import os
sys.path.insert(0, os.path.abspath('..'))
os.chdir(os.path.abspath('..'))

from novel_sources import cache

# 先清除缓存（确保重新获取）
chapter_url = "https://www.linovelib.com/novel/8/1843.html"
cache._content_cache = {}  # 清除内存缓存

# 手动清除文件缓存
import json
cache_file = os.path.join("cache", "content.json")
if os.path.exists(cache_file):
    with open(cache_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if chapter_url in data:
        del data[chapter_url]
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("已清除旧缓存")
    else:
        print("无旧缓存需要清除")

print(f"\n开始获取章节: {chapter_url}")
print("(这将启动 Playwright 浏览器)")

from novel_sources.linovelib import get_content
content = get_content(chapter_url)

lines = content.split('\n')
print(f"\n获取完成！总行数: {len(lines)}")
print(f"总字符数: {len(content)}")
print("\n前10行:")
for i, line in enumerate(lines[:10]):
    print(f"  {i+1:02d}: {line[:60]}")
print("\n后10行:")
for i, line in enumerate(lines[-10:]):
    print(f"  {len(lines)-10+i+1:02d}: {line[:60]}")

# 检查是否有重复
from collections import Counter
counter = Counter(lines)
dups = {t: c for t, c in counter.items() if c > 1 and t.strip()}
print(f"\n重复行数: {len(dups)}")
if dups:
    print("重复示例:")
    for t, c in list(dups.items())[:5]:
        print(f"  x{c}: {t[:50]}")

print("\n验证通过！" if len(dups) == 0 else "\n⚠️ 仍有重复段落！")
