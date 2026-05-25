"""
吉克文学小说源 (www.jkwxw.cc)
"""

import re
import threading
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from novel_sources import cache, robust_get

NAME = "吉克文学"
BASE_URL = "https://www.jkwxw.cc"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": BASE_URL,
}


def search(keyword: str) -> list[dict]:
    """搜索小说，返回 [{name, author, url}, ...]"""
    url = f"{BASE_URL}/search/"
    resp = robust_get(url, params={"searchkey": keyword}, headers=HEADERS)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")

    results = []
    seen = set()
    for a in soup.select("a"):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        # 匹配书本ID格式: /book_be65/
        m = re.match(r"^/book_([a-zA-Z0-9]+)/$", href)
        if m and text and m.group(1) not in seen:
            seen.add(m.group(1))
            
            # 提取作者
            author = "未知"
            parent = a.find_parent()
            if parent:
                author_a = parent.find("a", href=re.compile(r"/author/"))
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

    base_novel_url = novel_url.rstrip("/")
    page_url = f"{base_novel_url}/1/"

    chapters = []
    seen = set()

    # 最大循环 100 页以防止死循环
    for _ in range(100):
        resp = robust_get(page_url, headers=HEADERS)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")

        page_chapters = []
        for a in soup.select("a"):
            text = a.get_text(strip=True)
            href = a.get("href", "")

            # 处理吉克文学的 onclick 混淆机制: attrs={'href': 'javascript:;', 'onclick': "location.href='/book_be65/xhhx.html'"}
            onclick = a.get("onclick", "")
            m_onclick = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", onclick)
            if m_onclick:
                href = m_onclick.group(1)

            # 匹配章节后缀格式，且排重
            if href.endswith(".html") and "/book_" in href:
                full_ch_url = urljoin(BASE_URL, href)
                if full_ch_url not in seen:
                    seen.add(full_ch_url)
                    page_chapters.append({
                        "title": text,
                        "url": full_ch_url,
                    })

        if not page_chapters:
            break

        chapters.extend(page_chapters)

        # 匹配"下一页"链接
        next_page = None
        for a in soup.select("a"):
            if "下一页" in a.get_text(strip=True):
                href = a.get("href", "")
                onclick = a.get("onclick", "")
                m_onclick = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", onclick)
                if m_onclick:
                    href = m_onclick.group(1)
                
                if href and not href.startswith("javascript"):
                    next_page = urljoin(BASE_URL, href)
                    break

        if next_page and next_page != page_url:
            page_url = next_page
        else:
            break

    cache.set_chapters(novel_url, chapters)
    return chapters


def get_content(chapter_url: str) -> str:
    cached = cache.get_content(chapter_url)
    if cached:
        return cached

    resp = robust_get(chapter_url, headers=HEADERS)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")

    # 吉克文学的正文外层通常为 div#chaptercontent
    content_div = soup.select_one("div#chaptercontent") or soup.select_one("div.content")
    if not content_div:
        return "[内容获取失败]"

    for script in content_div.select("script"):
        script.decompose()

    text = content_div.get_text("\n", strip=True)
    # 清理网站小尾巴
    text = re.sub(r"天才一秒记住.*地址：.*?\n?", "", text, flags=re.IGNORECASE)
    
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
