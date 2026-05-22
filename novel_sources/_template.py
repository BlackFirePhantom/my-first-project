"""
新书源模板 — 复制此文件，改名后填入逻辑即可使用
只需实现 4 个东西: NAME, search, get_chapters, get_content
"""

from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# ── 源名称（显示在前端下拉框里）──
NAME = "示例源"

# ── 网站地址 ──
BASE_URL = "https://www.example.com"

# ── 请求头 ──
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": BASE_URL,
}


def search(keyword: str) -> list[dict]:
    """
    搜索小说
    返回: [{"name": "书名", "author": "作者", "url": "小说目录页URL"}, ...]
    """
    url = f"{BASE_URL}/search"
    resp = requests.get(url, params={"q": keyword}, headers=HEADERS, timeout=15)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")

    results = []
    # TODO: 根据实际网页结构修改 CSS 选择器
    for item in soup.select("这里换成实际的选择器"):
        a_tag = item.select_one("a")
        if a_tag:
            results.append({
                "name": a_tag.get_text(strip=True),
                "author": "未知",
                "url": urljoin(BASE_URL, a_tag["href"]),
            })
    return results


def get_chapters(novel_url: str, force_refresh: bool = False) -> list[dict]:
    """
    获取章节目录
    返回: [{"title": "章节标题", "url": "章节URL"}, ...]
    """
    resp = requests.get(novel_url, headers=HEADERS, timeout=15)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")

    chapters = []
    # TODO: 根据实际网页结构修改
    for a in soup.select("这里换成章节链接的选择器"):
        chapters.append({
            "title": a.get_text(strip=True),
            "url": urljoin(novel_url, a["href"]),
        })
    return chapters


def get_content(chapter_url: str) -> str:
    """
    获取章节正文（纯文本）
    """
    resp = requests.get(chapter_url, headers=HEADERS, timeout=15)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")

    # TODO: 根据实际网页结构修改
    content_div = soup.select_one("这里换成正文内容的选择器")
    if not content_div:
        return "[内容获取失败]"

    text = content_div.get_text("\n", strip=True)
    return text.strip()
