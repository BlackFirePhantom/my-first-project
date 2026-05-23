"""
腐书网小说源 (www.dadehe.com)
Playwright 绕过 Cloudflare，cookie 缓存 + 文件级正文/目录缓存
使用全局共享 Playwright 池（playwright_base），避免独立 browser 实例浪费内存。
"""

import re
import threading
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from novel_sources import cache, robust_get

NAME = "腐书网"
BASE_URL = "https://www.dadehe.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": BASE_URL,
}

# ── 内存预读缓存（热点数据，比文件更快）────────────────
_mem_content = {}
_mem_lock = threading.Lock()
PREFETCH_COUNT = 3

# ── Cloudflare 等待条件 ───────────────────────────────
_CF_WAIT_FN = "() => !document.title.includes('Just a moment')"


def _fetch_with_playwright(url: str) -> str:
    """使用共享 Playwright 池绕过 Cloudflare，并提取 CF cookie 缓存"""
    from novel_sources import playwright_base
    pool = playwright_base.get_pool()
    html = pool.fetch_html(url, wait_fn=_CF_WAIT_FN, wait_timeout=15000)

    # 提取并持久化 Cloudflare cookie（供后续 requests 直接使用）
    try:
        all_cookies = pool.get_cookies()
        cf_dict = {
            c["name"]: c["value"]
            for c in all_cookies
            if c.get("name") in ("cf_clearance", "__cf_bm", "is_human")
            and "dadehe.com" in c.get("domain", "")
        }
        if cf_dict:
            cache.set_meta("dadehe_cf_cookies", cf_dict, ttl=3600)
    except Exception as e:
        print(f"[dadehe] cookie 提取失败: {e}")

    return html


def _fetch_page(url: str) -> str:
    """优先 requests+cookie（快），失败回退共享 Playwright 池（慢）"""
    cookies = cache.get_meta("dadehe_cf_cookies") or {}

    if cookies:
        try:
            resp = requests.get(url, headers=HEADERS, cookies=cookies, timeout=10, verify=False)
            resp.encoding = "utf-8"
            if resp.status_code == 200 and "Just a moment" not in resp.text[:500]:
                return resp.text
        except Exception:
            pass

    return _fetch_with_playwright(url)


# 在模块导入时预热共享 Playwright 池（后台启动，不阻塞）
threading.Thread(
    target=lambda: __import__('novel_sources.playwright_base', fromlist=['get_pool']).get_pool(),
    daemon=True
).start()


# ── 搜索 ──────────────────────────────────────────────
def _get_human_cookie() -> dict:
    cached = cache.get_meta("dadehe_human_cookie")
    if cached:
        return cached

    session = requests.Session()
    session.headers.update(HEADERS)
    resp = session.get(
        f"{BASE_URL}/modules/article/search.php",
        params={"searchkey": "测试"},
        timeout=15,
    )
    m = re.search(r'encryptedCookieValue\s*=\s*"([^"]+)"', resp.text)
    if m:
        cookie = {"is_human": m.group(1).replace(r"\/", "/")}
        cache.set_meta("dadehe_human_cookie", cookie, ttl=1800)
        return cookie
    return {}


def search(keyword: str) -> list[dict]:
    if len(keyword) < 2:
        return []

    cookies = _get_human_cookie()
    resp = robust_get(
        f"{BASE_URL}/modules/article/search.php",
        params={"searchkey": keyword},
        headers=HEADERS,
        cookies=cookies,
    )

    if "访问验证" in resp.text:
        cache.set_meta("dadehe_human_cookie", {}, ttl=0)
        cookies = _get_human_cookie()
        resp = robust_get(
            f"{BASE_URL}/modules/article/search.php",
            params={"searchkey": keyword},
            headers=HEADERS,
            cookies=cookies,
        )

    soup = BeautifulSoup(resp.text, "lxml")
    results = []
    seen = set()
    for a in soup.select("a"):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        m = re.search(r"sovote\((\d+),\s*'(/(\d+)/)'\)", href)
        if m and text and len(text) > 1:
            novel_id = m.group(1)
            novel_path = m.group(2)
            if novel_id not in seen:
                seen.add(novel_id)
                author = "未知"
                parent = a.find_parent("li") or a.find_parent("div")
                if parent:
                    author_link = parent.find("a", href=re.compile(r"/fushuwangauthor/"))
                    if author_link:
                        author = author_link.get_text(strip=True)
                results.append({
                    "name": text,
                    "author": author,
                    "url": urljoin(BASE_URL, novel_path),
                })
    return results


# ── 章节目录 ──────────────────────────────────────────
def get_chapters(novel_url: str, force_refresh: bool = False) -> list[dict]:
    # 文件缓存
    if not force_refresh:
        cached = cache.get_chapters(novel_url)
        if cached:
            return cached

    m = re.search(r"/(\d+)/?", novel_url)
    if not m:
        return []
    novel_id = m.group(1)

    index_url = f"{BASE_URL}/{novel_id}/index.html"
    html = _fetch_page(index_url)
    soup = BeautifulSoup(html, "lxml")

    chapters = []
    for a in soup.select("div.CrListText a"):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        if f"/{novel_id}/" in href and ".html" in href:
            title = re.sub(r"\s+\d{4}-\d{2}-\d{2}.*$", "", text)
            chapters.append({
                "title": title.strip(),
                "url": urljoin(BASE_URL, href),
            })

    cache.set_chapters(novel_url, chapters)
    return chapters


# ── 正文 ──────────────────────────────────────────────
def _parse_content(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    content_div = soup.select_one("div#chaptercontent") or soup.select_one("div.chaptercontent")
    if not content_div:
        return "[内容获取失败]"

    for script in content_div.select("script"):
        script.decompose()

    for p in content_div.select("p"):
        txt = p.get_text(strip=True)
        style = p.get("style", "")
        if "display" in style and "none" in style:
            p.decompose()
            continue
        if any(k in txt for k in ["腐书网", "最新章节", "手机阅读", "天才一秒记住", "转码失败"]):
            p.decompose()
            continue

    text = content_div.get_text("\n", strip=True)
    text = re.sub(r"天才一秒记住.*?地址：.*?\n?", "", text)
    text = re.sub(r"手机阅读：.*?\n?", "", text)
    return text.strip()


def get_content(chapter_url: str) -> str:
    # 内存缓存（预读的热点数据）
    with _mem_lock:
        if chapter_url in _mem_content:
            return _mem_content[chapter_url]

    # 文件缓存
    cached = cache.get_content(chapter_url)
    if cached:
        with _mem_lock:
            _mem_content[chapter_url] = cached
        return cached

    html = _fetch_page(chapter_url)
    content = _parse_content(html)

    cache.set_content(chapter_url, content)
    with _mem_lock:
        _mem_content[chapter_url] = content
    return content


def prefetch(chapter_urls: list[str]):
    """后台预读后续章节"""
    def _do_prefetch():
        for url in chapter_urls:
            with _mem_lock:
                if url in _mem_content:
                    continue
            if cache.get_content(url):
                continue
            try:
                html = _fetch_page(url)
                content = _parse_content(html)
                cache.set_content(url, content)
                with _mem_lock:
                    _mem_content[url] = content
            except Exception:
                pass

    threading.Thread(target=_do_prefetch, daemon=True).start()


def clear_cache():
    with _mem_lock:
        _mem_content.clear()
