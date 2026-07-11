"""
蚂蚁文学小说源 (www.mayiwsk.com)
"""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from novel_sources import cache, robust_get, prefetch_concurrent

NAME = "蚂蚁文学"
BASE_URL = "https://www.mayiwsk.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": BASE_URL,
}


def search(keyword: str) -> list[dict]:
    """搜索小说，返回 [{name, author, url}, ...]"""
    url = f"{BASE_URL}/modules/article/search.php"
    resp = robust_get(url, params={"searchkey": keyword}, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "lxml")

    results = []
    seen = set()
    for a in soup.select("a"):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        # 匹配书本ID格式: /66_66337/
        m = re.match(r"^/(\d+_\d+)/$", href)
        if m and text and m.group(1) not in seen:
            seen.add(m.group(1))
            
            # 提取作者
            author = "未知"
            tr = a.find_parent("tr")
            if tr:
                tds = tr.find_all("td")
                if len(tds) > 2:
                    author = tds[2].get_text(strip=True)
                    
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
    soup = BeautifulSoup(resp.text, "lxml")

    m = re.search(r"/(\d+_\d+)/?$", novel_url)
    if not m:
        return []
    novel_id = m.group(1)

    chapters = []
    seen = set()
    for a in soup.select("a"):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        # 匹配章节链接格式: /119_119581/58305147.html
        pattern = rf"^/{novel_id}/(\d+)\.html$"
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
    soup = BeautifulSoup(resp.text, "lxml")

    content_div = soup.select_one("div#content")
    if not content_div:
        return "[内容获取失败]"

    for script in content_div.select("script"):
        script.decompose()

    text = content_div.get_text("\n", strip=True)
    # 清理网站自带的广告及提示语
    text = re.sub(r"最新网址：www\.mayiwsk\.com\n?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"本站域名www\.mayiwsk\.com\n?", "", text, flags=re.IGNORECASE)
    
    text = text.strip()
    cache.set_content(chapter_url, text)
    return text


def prefetch(chapter_urls: list[str]):
    """后台并发预读后续章节"""
    prefetch_concurrent(get_content, chapter_urls)
