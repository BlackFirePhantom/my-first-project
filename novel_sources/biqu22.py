"""
22笔趣阁小说源 (www.22biqu.com)
"""

import re
import threading
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from novel_sources import cache, robust_get, robust_post

NAME = "22笔趣阁"
BASE_URL = "https://www.22biqu.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": BASE_URL,
}


def search(keyword: str) -> list[dict]:
    """搜索小说，返回 [{name, author, url}, ...]"""
    resp = robust_post(
        f"{BASE_URL}/ss/",
        data={"searchkey": keyword},
        headers=HEADERS,
    )
    soup = BeautifulSoup(resp.text, "lxml")

    results = []
    seen = set()
    for a in soup.select("a"):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        # 小说链接: /biquID/
        m = re.match(r"^/biqu(\d+)/$", href)
        if m and text and len(text) > 1 and m.group(1) not in seen:
            seen.add(m.group(1))
            results.append({
                "name": text,
                "author": "未知",
                "url": urljoin(BASE_URL, href),
            })
    return results


def get_chapters(novel_url: str, force_refresh: bool = False) -> list[dict]:
    if not force_refresh:
        cached = cache.get_chapters(novel_url)
        if cached:
            return cached

    chapters = []
    seen = set()
    page_url = novel_url.rstrip("/")

    for _ in range(100):
        resp = robust_get(page_url + "/", headers=HEADERS)
        soup = BeautifulSoup(resp.text, "lxml")

        # 只从目录区域取章节，跳过顶部的"最新章节"
        section = soup.select_one("div.row.row-section")
        if not section:
            break

        # section-box[0] 是"最新章节"（每页重复），跳过；box[1] 是正文目录
        boxes = section.select("div.section-box")
        target_boxes = boxes[1:] if len(boxes) > 1 else boxes

        for box in target_boxes:
            for a in box.select("a"):
                href = a.get("href", "")
                text = a.get_text(strip=True)
                if re.match(r"/biqu\d+/\d+\.html$", href) and text and href not in seen:
                    seen.add(href)
                    chapters.append({
                        "title": text.strip(),
                        "url": urljoin(BASE_URL, href),
                    })

        # 找"下一页"链接
        next_page = None
        for a in section.select("a"):
            if "下一" in a.get_text(strip=True):
                next_page = a.get("href", "").rstrip("/")
                break

        if next_page:
            page_url = BASE_URL + next_page
        else:
            break

    cache.set_chapters(novel_url, chapters)
    return chapters


def get_content(chapter_url: str) -> str:
    cached = cache.get_content(chapter_url)
    if cached:
        return cached

    all_text = []
    page_url = chapter_url

    for _ in range(10):
        resp = robust_get(page_url, headers=HEADERS)
        soup = BeautifulSoup(resp.text, "lxml")

        content_div = soup.select_one("div#content")
        if not content_div:
            break

        for script in content_div.select("script"):
            script.decompose()

        all_text.append(content_div.get_text("\n", strip=True))

        # 找"下一页"链接（分页格式: chapterID_2.html）
        next_page = None
        for a in soup.select("a"):
            if "下一" in a.get_text(strip=True):
                href = a.get("href", "")
                if re.search(r"_\d+\.html$", href):
                    next_page = urljoin(BASE_URL, href)
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

