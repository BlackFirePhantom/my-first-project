"""
逐页追踪，找出重复段落是由哪一页产生的
"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import sys, os
sys.path.insert(0, os.path.abspath('.'))

from novel_sources.linovelib import _fetch_chapter_data
from bs4 import BeautifulSoup
from collections import Counter

urls = [
    "https://www.linovelib.com/novel/8/1843.html",
    "https://www.linovelib.com/novel/8/1843_2.html",
    "https://www.linovelib.com/novel/8/1843_3.html",
    "https://www.linovelib.com/novel/8/1843_4.html",
    "https://www.linovelib.com/novel/8/1843_5.html",
]

base_chapter_id = "1843"
all_paragraphs = []

for i, url in enumerate(urls):
    print(f"\n=== 处理第 {i+1} 页: {url.split('/')[-1]} ===")
    data = _fetch_chapter_data(url)
    inner_html = data.get("innerHtml", "")
    next_page = data.get("nextPage", None)
    
    soup = BeautifulSoup(inner_html, "lxml")
    ps = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
    
    # 检查该页内部重复
    counter_page = Counter(ps)
    internal_dups = {t: c for t, c in counter_page.items() if c > 1}
    print(f"  本页段落数: {len(ps)}, 内部重复: {len(internal_dups)}")
    
    # 检查和已有段落的重复
    page_paragraphs = ps
    if all_paragraphs and page_paragraphs:
        overlap_found = 0
        window = min(5, len(all_paragraphs), len(page_paragraphs))
        for size in range(window, 0, -1):
            if all_paragraphs[-size:] == page_paragraphs[:size]:
                overlap_found = size
                break
        print(f"  跨页重叠段落（连续尾部匹配）: {overlap_found}")
        if overlap_found:
            page_paragraphs = page_paragraphs[overlap_found:]
    
    # 检查和已有段落的非连续重复
    all_set = set(all_paragraphs)
    scattered_dups = [t for t in page_paragraphs if t in all_set]
    print(f"  散布式重复（该页段落已在之前出现过）: {len(scattered_dups)}")
    if scattered_dups:
        print("  示例:")
        for t in scattered_dups[:3]:
            print(f"    {t[:60]}")
    
    all_paragraphs.extend(page_paragraphs)
    print(f"  累计段落数: {len(all_paragraphs)}")
    print(f"  下一页: {next_page}")
    
    # 检查整体重复
    counter_all = Counter(all_paragraphs)
    current_dups = {t: c for t, c in counter_all.items() if c > 1}
    print(f"  当前累计重复数: {len(current_dups)}")
