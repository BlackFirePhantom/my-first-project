"""
笔趣阁小说源 (www.xbiquge.info)
"""

import re
import threading
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from novel_sources import cache, robust_get

NAME = "笔趣阁"
BASE_URL = "https://www.xbiquge.info"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": BASE_URL,
}


def search(keyword: str) -> list[dict]:
    """搜索小说，返回 [{name, author, url}, ...]"""
    url = f"{BASE_URL}/search.php"
    resp = robust_get(url, params={"q": keyword}, headers=HEADERS)
    soup = BeautifulSoup(resp.text, "lxml")

    results = []
    seen = set()
    for a in soup.select("a"):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        # 匹配小说链接: /XX/XXXXX/
        m = re.match(r"^/(\d+)/(\d+)/$", href)
        if m and text and len(text) > 1:
            novel_id = m.group(2)
            if novel_id not in seen:
                seen.add(novel_id)
                # 书名去掉 [分类] 前缀
                name = re.sub(r"^\[.*?\]", "", text).strip()
                results.append({
                    "name": name,
                    "author": "未知",
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

    chapters = []
    seen = set()
    for a in soup.select("a"):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        if re.match(r"^/\d+/\d+/\d+\.html$", href) and text and href not in seen:
            seen.add(href)
            chapters.append({
                "title": text.strip(),
                "url": urljoin(BASE_URL, href),
            })

    cache.set_chapters(novel_url, chapters)
    return chapters


def get_content(chapter_url: str) -> str:
    cached = cache.get_content(chapter_url)
    if cached:
        return cached

    all_text = []
    page_url = chapter_url
    max_pages = 10  # 防止死循环

    for _ in range(max_pages):
        resp = robust_get(page_url, headers=HEADERS)
        soup = BeautifulSoup(resp.text, "lxml")

        article = soup.select_one("article")
        if not article:
            break

        for script in article.select("script"):
            script.decompose()

        page_text = article.get_text("\n", strip=True)
        # 去掉页码标记，如 "第(1/3)页"
        page_text = re.sub(r"第?\(\d+/\d+\)页\s*", "", page_text)
        all_text.append(page_text.strip())

        # 找"下一章"链接，判断是否还有下一页
        next_page = None
        for a in soup.select("a"):
            if "下一" in a.get_text(strip=True):
                href = a.get("href", "")
                basename = href.rsplit("/", 1)[-1]
                # 分页链接: 374419_2.html, 374419_3.html
                if re.match(r"\d+_\d+\.html$", basename):
                    next_page = urljoin(BASE_URL, href)
                    break
                # 章节链接说明已经是最后一页
                elif re.match(r"/\d+/\d+/\d+\.html$", href):
                    next_page = None
                    break

        if next_page:
            page_url = next_page
        else:
            break

    content = "\n".join(all_text).strip() or "[内容获取失败]"
    cache.set_content(chapter_url, content)
    return content


def prefetch(chapter_urls: list[str]):
    """后台预读后续章节"""
    def _do_prefetch():
        for url in chapter_urls:
            try:
                get_content(url)
            except Exception:
                pass

    threading.Thread(target=_do_prefetch, daemon=True).start()

