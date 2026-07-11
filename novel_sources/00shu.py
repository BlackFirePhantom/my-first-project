"""
00小说网小说源 (m.00shu.la)

URL 规律小结（实测归纳）：
- 搜索：   GET /s.php?searchkey={keyword}          （UTF-8，只接受 searchkey 参数名）
- 详情页： /book/{bookID}/                          （同时是目录第一页）
- 目录页： /{prefix}/{bookID}_{page}/               （prefix = bookID 前 2 位，page>=2）
           每页约 25 章，用页面里的"下一页"链接判断终止
- 章节页： /{prefix}/{bookID}/{chapterID}.html
- 章节翻页：/{prefix}/{bookID}/{chapterID}_{N}.html  （每章可能分多页）

注意点：
1. 搜索结果页只接受 `searchkey` 这一个参数名，`q/wd/keyword` 都会返回空结果页。
2. 详情页本身含"最新章节预览"（页首）+ 正文目录（页中）两块，且首章链接通常重复出现
   两次（一次叫"从头阅读"，一次是真实章节标题），需按 URL 全局去重。
3. 章节正文用 `div#novelcontent.novelcontent` 容器，正文页码提示 `(第X/Y页)` 与站名
   "最新网址：m.00shu.la" 需要清理掉。
4. 章节翻页第 N+1 页即使无内容也会返回 200，必须用"下一页"链接是否存在来判断终止。
"""

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from novel_sources import cache, robust_get, robust_post, prefetch_concurrent

NAME = "00小说网"
BASE_URL = "https://m.00shu.la"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": BASE_URL,
}

# 详情页/搜索结果里的非章节文字，遇到这些就跳过
_NON_CHAPTER_TEXT = {"从头阅读", "正文", "最新章节", "最新章节预览", "全本目录"}

# 章节链接正则：/{prefix}/{bookID}/{chapterID}.html  或 _N.html（分页）
_CHAPTER_HREF_RE = re.compile(r"^/(\d+)/(\d+)/(\d+)(?:_\d+)?\.html$")

# 站名/分页提示清理
_SITE_TAIL_RE = re.compile(r"最新网址[：:]\s*[^\n]*\n?", re.IGNORECASE)
_PAGE_HINT_RE = re.compile(r"\(第\s*\d+\s*/\s*\d+\s*页\)")

# 章节分页中断提示："（本章未完，请点击下一页继续阅读）"
_INCOMPLETE_HINT_RE = re.compile(r"[（(]\s*本章未完[^（）()]*?继续阅读[^（）()]*?[)）]", re.IGNORECASE)

# 占位符（"正在手打中"等）——这种章节实际没有正文，应判定为获取失败
_PLACEHOLDER_RE = re.compile(r"(正在手打中|内容更新后.*重新刷新|请稍等片刻.*获取最新更新)", re.IGNORECASE)

# 兜底清理的导航词行（容器内 a / ul.novelbutton 已 decompose，这里防边缘情况混入）
_NAV_LINE_RE = re.compile(
    r"^(上一章|下一章|上一页|下一页|返回目录|返回书页|加入书架|进入书架|加入书签|目录)\s*$"
)


# ── 工具 ──────────────────────────────────────────────
def _parse(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def _find_next_page(soup: BeautifulSoup) -> str | None:
    """提取页面里的"下一页"链接 href，无则返回 None"""
    for a in soup.select("a"):
        if "下一页" in a.get_text(strip=True):
            href = a.get("href", "").strip()
            if href and not href.lower().startswith("javascript"):
                return href
    return None


# ── 搜索 ──────────────────────────────────────────────
def search(keyword: str) -> list[dict]:
    """搜索小说，返回 [{name, author, url}, ...]"""
    data = {
        "searchkey": keyword,
        "type": "articlename"
    }
    resp = robust_post(f"{BASE_URL}/s.php", data=data, headers=HEADERS, timeout=8, retries=1)
    resp.encoding = "utf-8"
    soup = _parse(resp.text)

    results = []
    seen = set()
    for p in soup.select("p.sone"):
        a = p.select_one("a")
        if not a:
            continue
        href = a.get("href", "")
        # 只接受 /book/{ID}/ 这种格式的结果
        if not re.match(r"^/book/\d+/?$", href):
            continue
        name = a.get_text(strip=True)
        if not name or href in seen:
            continue
        seen.add(href)

        # 作者在 span.author a
        author = "未知"
        author_a = p.select_one("span.author a")
        if author_a:
            author_text = author_a.get_text(strip=True)
            if author_text and author_text != name:
                author = author_text

        results.append({
            "name": name,
            "author": author,
            "url": urljoin(BASE_URL, href),
        })
    return results


# ── 目录 ──────────────────────────────────────────────
def _extract_book_id(novel_url: str) -> str | None:
    """从 /book/{ID}/ 提取 bookID"""
    m = re.search(r"/book/(\d+)/?", novel_url)
    return m.group(1) if m else None


def _scan_chapter_links(soup: BeautifulSoup, book_id: str) -> list[tuple[str, str]]:
    """从一页 HTML 抽出 (相对 href, 标题)，按 URL 去重，跳过伪章节文字"""
    found = []
    seen = set()
    # 章节链接前缀不固定，只要求第二段等于 bookID
    pattern = re.compile(rf"^/\d+/{book_id}/\d+\.html$")
    for a in soup.select("a"):
        href = a.get("href", "")
        text = a.get_text(strip=True)
        if not pattern.match(href) or not text:
            continue
        # 排除"从头阅读"等非章节标题（它们 href 是第一章，标题不是章节名）
        if text in _NON_CHAPTER_TEXT or text.startswith("最新章节"):
            continue
        if href in seen:
            continue
        seen.add(href)
        found.append((href, text))
    return found


def get_chapters(novel_url: str, force_refresh: bool = False) -> list[dict]:
    """获取章节目录，自动翻页至结尾"""
    if not force_refresh:
        cached = cache.get_chapters(novel_url)
        if cached:
            return cached

    book_id = _extract_book_id(novel_url)
    if not book_id:
        return []

    chapters: list[dict] = []
    seen_urls: set[str] = set()
    page_url = novel_url  # 第一页就是 /book/{ID}/
    visited_pages: set[str] = set()

    # 防止异常情况下死循环
    for _ in range(200):
        if page_url in visited_pages:
            break
        visited_pages.add(page_url)

        resp = robust_get(page_url, headers=HEADERS)
        resp.encoding = "utf-8"
        soup = _parse(resp.text)

        page_chapters = _scan_chapter_links(soup, book_id)
        for href, title in page_chapters:
            if href in seen_urls:
                continue
            seen_urls.add(href)
            chapters.append({
                "title": title,
                "url": urljoin(BASE_URL, href),
            })

        next_href = _find_next_page(soup)
        if not next_href or next_href in visited_pages:
            break
        page_url = urljoin(BASE_URL, next_href)

    cache.set_chapters(novel_url, chapters)
    return chapters


# ── 正文 ──────────────────────────────────────────────
def get_content(chapter_url: str) -> str:
    """获取章节正文（自动合并分页）"""
    cached = cache.get_content(chapter_url)
    if cached:
        return cached

    parts: list[str] = []
    page_url = chapter_url
    visited: set[str] = set()

    for _ in range(50):  # 兜底防死循环，单章一般不会超过几页
        if page_url in visited:
            break
        visited.add(page_url)

        resp = robust_get(page_url, headers=HEADERS)
        resp.encoding = "utf-8"
        soup = _parse(resp.text)

        # 正文容器：div#novelcontent.novelcontent
        content_div = soup.select_one("div#novelcontent") or soup.select_one("div.novelcontent")
        if not content_div:
            break

        # 清掉脚本/样式/广告、容器内导航 <a>、底部导航条 ul.novelbutton、
        # 以及反复出现的站名提示 div#content_tip
        for tag in content_div.select(
            "script, style, ins, a, ul.novelbutton, div#content_tip"
        ):
            tag.decompose()

        text = content_div.get_text("\n", strip=True)
        # 清理"最新网址：m.00shu.la"站名尾巴与 "(第X/Y页)" 提示
        text = _SITE_TAIL_RE.sub("", text)
        text = _PAGE_HINT_RE.sub("", text)
        # 清理章节分页处的"（本章未完，请点击下一页继续阅读）"
        text = _INCOMPLETE_HINT_RE.sub("", text)
        # 兜底：清理残留的导航词行
        text = "\n".join(
            line for line in text.split("\n")
            if line.strip() and not _NAV_LINE_RE.match(line.strip())
        )
        if text:
            parts.append(text)

        # 下一页：章节自身的分页 _N.html
        next_href = _find_next_page(soup)
        if not next_href or next_href in visited:
            break
        page_url = urljoin(BASE_URL, next_href)

    content = "\n".join(parts).strip()
    if not content:
        return "[内容获取失败]"
    # 识别"正在手打中"等占位符——章节存在但正文尚未录入
    if _PLACEHOLDER_RE.search(content) and len(content) < 200:
        return "[本章暂未录入正文，请稍后重试]"

    # 去掉开头的章节标题提示（正文首行经常是 "0001【这题好难，我不会做！】"，
    # 与 reader.html 已显示的章节标题重复，这里不强删，交给前端处理）

    cache.set_content(chapter_url, content)
    return content


def prefetch(chapter_urls: list[str]):
    """后台并发预读后续章节"""
    prefetch_concurrent(get_content, chapter_urls)
