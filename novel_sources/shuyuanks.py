"""
书源阁小说源 (www.shuyuanks.com)
"""

import re
import threading
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from novel_sources import cache, robust_get

NAME = "书源阁"
BASE_URL = "https://www.shuyuanks.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": BASE_URL,
}


def search(keyword: str) -> list[dict]:
    """搜索小说，返回 [{name, author, url}, ...]"""
    url = f"{BASE_URL}/search/"
    resp = robust_get(url, params={"keyword": keyword}, headers=HEADERS)
    # 搜索页通常也是 UTF-8，如果是 GBK 我们可以做自适应
    if "charset=gb" in resp.headers.get("Content-Type", "").lower():
        resp.encoding = "gb18030"
    else:
        resp.encoding = "utf-8"
        
    soup = BeautifulSoup(resp.text, "lxml")

    results = []
    seen = set()
    for a in soup.select("a"):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        # 匹配书本ID格式: /content/113668.html
        m = re.match(r"^/content/(\d+)\.html$", href)
        if m and text and m.group(1) not in seen:
            seen.add(m.group(1))
            
            # 提取作者
            author = "未知"
            parent = a.find_parent()
            if parent:
                parent_text = parent.get_text(" | ", strip=True)
                # 寻找形如 "作者: 某某" 或是 "/user/xx-profile/"
                m_author = re.search(r"作者\s*[：:]\s*([^|]+)", parent_text)
                if m_author:
                    author = m_author.group(1).strip()
                else:
                    author_a = parent.find("a", href=re.compile(r"/user/"))
                    if author_a:
                        author = author_a.get_text(strip=True)
                    
            results.append({
                "name": text,
                "author": author,
                "url": urljoin(BASE_URL, href),
            })
    return results


def get_chapters(novel_url: str, force_refresh: bool = False) -> list[dict]:
    if not force_refresh:
        cached = cache.get_chapters(novel_url)
        if cached:
            return cached

    resp = robust_get(novel_url, headers=HEADERS)
    if "charset=gb" in resp.headers.get("Content-Type", "").lower():
        resp.encoding = "gb18030"
    else:
        resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")

    m = re.search(r"/content/(\d+)\.html$", novel_url)
    if not m:
        return []
    novel_id = m.group(1)

    chapters = []
    seen = set()
    for a in soup.select("a"):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        # 匹配章节链接格式: /novel/113668/1.html
        pattern = rf"^/novel/{novel_id}/(\d+)\.html$"
        if re.match(pattern, href) and text and href not in seen:
            seen.add(href)
            chapters.append({
                "title": text,
                "url": urljoin(BASE_URL, href),
            })

    cache.set_chapters(novel_url, chapters)
    return chapters


def get_content(chapter_url: str) -> str:
    cached = cache.get_content(chapter_url)
    if cached:
        return cached

    resp = robust_get(chapter_url, headers=HEADERS)
    if "charset=gb" in resp.headers.get("Content-Type", "").lower():
        resp.encoding = "gb18030"
    else:
        resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")

    content_div = soup.select_one("div.content") or soup.select_one("div#content")
    if not content_div:
        return "[内容获取失败]"

    for script in content_div.select("script"):
        script.decompose()

    text = content_div.get_text("\n", strip=True)
    # 清理转码提示广告等
    text = re.sub(r"如果出现文字缺失.*退出阅读模式\n?", "", text, flags=re.IGNORECASE)
    
    text = text.strip()
    cache.set_content(chapter_url, text)
    return text


def prefetch(chapter_urls: list[str]):
    """后台预读后续章节"""
    def _do_prefetch():
        for url in chapter_urls:
            try:
                get_content(url)
            except Exception:
                pass

    threading.Thread(target=_do_prefetch, daemon=True).start()
