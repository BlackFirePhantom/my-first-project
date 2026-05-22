"""
哔哩轻小说源 (www.linovelib.com)
直接 requests 抓取目录/搜索，使用后台 Playwright (offscreen) 获取正文以绕过内容截断与加密限制。
"""

import re
import time
import atexit
import threading
from queue import Queue
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from novel_sources import cache, robust_get

NAME = "哔哩轻小说"
BASE_URL = "https://www.linovelib.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": BASE_URL,
}

# ── Playwright 后台进程管理 ─────────────────────────
_worker_thread = None
_task_queue = Queue()
_ready = threading.Event()


def _worker():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    browser = pw.chromium.launch(
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--window-position=-32000,-32000",
            "--window-size=10,10"
        ],
    )
    context = browser.new_context(
        user_agent=HEADERS["User-Agent"],
        viewport={"width": 1024, "height": 768},
    )
    context.add_init_script(
        'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    )
    _ready.set()

    while True:
        task = _task_queue.get()
        if task is None:
            break
        url, result_box = task
        mode = result_box.get("_mode", "html")  # 'html' 或 'chapter'
        try:
            print(f"[Worker] Opening page ({mode}): {url}")
            page = context.new_page()
            try:
                page.goto(url, timeout=30000)
                # 等待正文元素渲染完成
                page.wait_for_function(
                    "() => { "
                    "  const el = document.querySelector('div#mlfy_main_text'); "
                    "  if (!el || !el.innerText) return false; "
                    "  const text = el.innerText; "
                    "  return !text.includes('內容加載失敗') && "
                    "         !text.includes('内容加载失败') && "
                    "         !text.includes('数据缺失') && "
                    "         !text.includes('正在加载'); "
                    "}",
                    timeout=15000
                )
                if mode == "chapter":
                    # 直接在浏览器 JS 环境中提取数据，避免拿到被混淆 JS 修改的序列化 HTML
                    data = page.evaluate("""
                        () => {
                            // 获取 #TextContent 的 innerHTML（JS 执行前的原始内容）
                            const container = document.querySelector('#TextContent');
                            const innerHtml = container ? container.innerHTML : '';

                            // 获取"下一页"链接
                            let nextPage = null;
                            const links = document.querySelectorAll('.mlfy_page a');
                            for (const a of links) {
                                const t = a.innerText.trim();
                                if (t.includes('下一页') || t.includes('下一章')) {
                                    nextPage = a.href;
                                    break;
                                }
                            }
                            return { innerHtml, nextPage };
                        }
                    """)
                    result_box["chapter_data"] = data
                else:
                    result_box["html"] = page.content()
            finally:
                page.close()
        except Exception as e:
            print(f"[Worker] Exception for {url}: {e}")
            result_box["error"] = e

    try:
        browser.close()
        pw.stop()
    except Exception:
        pass


def _start_worker_async():
    global _worker_thread
    if _worker_thread is None or not _worker_thread.is_alive():
        _worker_thread = threading.Thread(target=_worker, daemon=True)
        _worker_thread.start()
        atexit.register(lambda: _task_queue.put(None))


def _ensure_worker():
    _start_worker_async()
    _ready.wait(timeout=30)


def _fetch_with_playwright(url: str) -> str:
    """获取整页 HTML（保留用于需要完整页面的场合）"""
    _ensure_worker()
    result_box = {"_mode": "html"}
    _task_queue.put((url, result_box))
    for _ in range(600):
        if "html" in result_box or "error" in result_box:
            break
        time.sleep(0.1)
    if "error" in result_box:
        raise result_box["error"]
    return result_box.get("html", "[页面获取超时]")


def _fetch_chapter_data(url: str) -> dict:
    """
    在 Playwright 浏览器中直接通过 JS evaluate() 提取章节数据。
    直接获取 #TextContent 的 innerHTML 和下一页链接，
    完全避免 page.content() 返回被混淆 JS 修改的序列化 DOM。
    返回: {"innerHtml": str, "nextPage": str or None}
    """
    _ensure_worker()
    result_box = {"_mode": "chapter"}
    _task_queue.put((url, result_box))
    for _ in range(600):
        if "chapter_data" in result_box or "error" in result_box:
            break
        time.sleep(0.1)
    if "error" in result_box:
        raise result_box["error"]
    return result_box.get("chapter_data", {"innerHtml": "", "nextPage": None})


# ── 书源基础功能接口 ──────────────────────────────────

def search(keyword: str) -> list[dict]:
    """
    搜索小说。
    由于 Cloudflare Turnstile 限制关键字搜索，故支持以下 fallback:
    1. 若 keyword 是网址 (包含 linovelib.com 或 bilinovel.com):
       - 直接请求该网址提取小说信息。
    2. 若 keyword 是纯数字 ID (例如 1):
       - 补全为 https://www.linovelib.com/novel/1.html 请求小说信息。
    3. 若 keyword 是 "novel/1.html" 等形式:
       - 补全为 https://www.linovelib.com/novel/1.html 请求。
    """
    keyword = keyword.strip()
    target_url = None

    # 判断是否是 URL
    if keyword.startswith("http://") or keyword.startswith("https://") or "linovelib.com" in keyword or "bilinovel.com" in keyword:
        # 如果没有 http，补齐 http
        if not keyword.startswith("http"):
            target_url = "https://" + keyword
        else:
            target_url = keyword
    elif keyword.isdigit():
        target_url = f"https://www.linovelib.com/novel/{keyword}.html"
    elif re.match(r"^novel/\d+(\.html)?$", keyword):
        if not keyword.endswith(".html"):
            keyword += ".html"
        target_url = f"https://www.linovelib.com/{keyword}"
    
    if target_url:
        # 获取小说元数据
        try:
            resp = robust_get(target_url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                raise Exception(f"请求失败，状态码: {resp.status_code}")
            
            soup = BeautifulSoup(resp.text, "lxml")
            
            # 使用 og 标签提取，最准确且不受改版影响
            title_meta = soup.find("meta", property="og:title")
            author_meta = soup.find("meta", property="og:novel:author") or soup.find("meta", name="author")
            
            novel_name = title_meta["content"] if title_meta else None
            if not novel_name:
                # 尝试普通选择器
                name_tag = soup.select_one("h1.book-name, h1#name, div.book-info h1, h1")
                novel_name = name_tag.get_text(strip=True) if name_tag else "未知"
                
            novel_author = author_meta["content"] if author_meta else None
            if not novel_author:
                author_tag = soup.select_one("div.book-author, a.writer, .author")
                if author_tag:
                    novel_author = re.sub(r"^作者[：:]\s*", "", author_tag.get_text(strip=True))
                else:
                    novel_author = "未知"
            
            # 确保 URL 的域跟 target_url 一致
            parsed_target = urlparse(target_url)
            novel_id = target_url.split("/novel/")[-1].split(".")[0].split("/")[0]
            novel_url = f"{parsed_target.scheme}://{parsed_target.netloc}/novel/{novel_id}.html"
            
            return [{
                "name": novel_name,
                "author": novel_author,
                "url": novel_url
            }]
        except Exception as e:
            raise Exception(f"解析小说详情页失败: {e}")
            
    # 关键字搜索拦截
    raise Exception(
        "哔哩轻小说由于 Cloudflare 拦截无法直接进行关键词搜索。\n"
        "请直接在此处输入小说详情页网址或小说 ID，格式支持以下几种：\n"
        "1. 完整链接，如：https://www.linovelib.com/novel/1.html\n"
        "2. 镜像站链接，如：https://www.bilinovel.com/novel/1.html\n"
        "3. 纯数字 ID，如：1"
    )


def get_chapters(novel_url: str, force_refresh: bool = False) -> list[dict]:
    """获取小说所有章节目录"""
    if not force_refresh:
        cached = cache.get_chapters(novel_url)
        if cached:
            return cached
            
    # 构造目录 URL
    if "/catalog" in novel_url:
        catalog_url = novel_url
    elif novel_url.endswith(".html"):
        catalog_url = novel_url.replace(".html", "/catalog")
    else:
        catalog_url = novel_url.rstrip("/") + "/catalog"
        
    # 获取目录 HTML
    resp = robust_get(catalog_url, headers=HEADERS, timeout=15)
    if resp.status_code != 200:
        raise Exception(f"获取目录失败，状态码: {resp.status_code}")
        
    soup = BeautifulSoup(resp.text, "lxml")
    
    # 提取小说名称，以便用于去除卷标题中的小说名
    novel_name_meta = soup.find("meta", property="og:novel:book_name")
    novel_name = novel_name_meta["content"] if novel_name_meta else None
    
    chapters = []
    
    # 遍历每个卷 volume 容器
    volumes = soup.select(".volume-list > .volume")
    if not volumes:
        # Fallback: 如果没有 .volume 结构，直接找所有的 a
        seen = set()
        for a in soup.select("ul.chapter-list li a, li.col-4 a, a"):
            href = a.get("href", "")
            text = a.get_text(strip=True)
            if href and text and "/novel/" in href and ".html" in href and "vol_" not in href:
                full_url = urljoin(catalog_url, href)
                if full_url not in seen:
                    seen.add(full_url)
                    chapters.append({
                        "title": text,
                        "url": full_url
                    })
    else:
        for vol in volumes:
            # 提取卷标题
            vol_info = vol.select_one(".volume-info h2.v-line")
            vol_title = vol_info.get_text(strip=True) if vol_info else ""
            
            # 去除卷标题中冗余的书名前缀
            if vol_title and novel_name and vol_title.startswith(novel_name):
                vol_title = vol_title[len(novel_name):].strip()
                
            # 提取卷下的所有章节链接
            for a in vol.select("ul.chapter-list li a"):
                href = a.get("href", "")
                text = a.get_text(strip=True)
                if href and text and "vol_" not in href:
                    full_url = urljoin(catalog_url, href)
                    
                    # 拼接标题，如 "[1 旧校舍的恶魔] 插图"
                    title = f"[{vol_title}] {text}" if vol_title else text
                    chapters.append({
                        "title": title,
                        "url": full_url
                    })
                    
    cache.set_chapters(novel_url, chapters)
    return chapters


def get_content(chapter_url: str) -> str:
    """获取章节正文（使用 Playwright 直接提取 #TextContent.innerHTML，支持多页合并）"""
    cached = cache.get_content(chapter_url)
    if cached:
        return cached
        
    all_paragraphs = []
    page_url = chapter_url
    max_pages = 25  # 防止死循环
    
    # 提取当前章节的基准 ID（用于判断"下一页"是否属于同一章）
    basename = chapter_url.split("/")[-1].split(".")[0]
    base_chapter_id = basename.split("_")[0]
    
    for _ in range(max_pages):
        # 使用新的 chapter 模式：在浏览器 JS 中直接获取 innerHTML 和 nextPage
        data = _fetch_chapter_data(page_url)
        inner_html = data.get("innerHtml", "")
        next_page_raw = data.get("nextPage", None)
        
        if not inner_html:
            break
            
        # 用 BeautifulSoup 解析纯净的 #TextContent innerHTML
        soup = BeautifulSoup(inner_html, "lxml")
        
        # 清理无用标签与注音/拼音
        for el in soup.select("script, .dag"):
            el.decompose()
        for rt in soup.select("rt"):
            rt.decompose()
            
        # 提取段落（innerHTML 中段落已是正确顺序，无混淆克隆）
        p_tags = soup.find_all("p")
        page_paragraphs = []
        if p_tags:
            for p in p_tags:
                txt = p.get_text(strip=True)
                if txt:
                    page_paragraphs.append(txt)
        else:
            txt = soup.get_text("\n", strip=True)
            if txt:
                page_paragraphs = [line.strip() for line in txt.split("\n") if line.strip()]
        
        # 处理跨页重叠：某些网站会在下一页开头重复上一页末尾的段落
        # 用"尾部滑动窗口"检测：如果新页前 N 段与当前末尾 N 段完全匹配，就跳过这段重叠
        if all_paragraphs and page_paragraphs:
            overlap_found = 0
            # 最多检测前 5 段是否重叠
            window = min(5, len(all_paragraphs), len(page_paragraphs))
            for size in range(window, 0, -1):
                tail = all_paragraphs[-size:]
                head = page_paragraphs[:size]
                if tail == head:
                    overlap_found = size
                    break
            if overlap_found:
                page_paragraphs = page_paragraphs[overlap_found:]
        
        all_paragraphs.extend(page_paragraphs)

        
        # 判断"下一页"链接是否属于同一章节
        next_page_url = None
        if next_page_raw:
            # next_page_raw 是浏览器 JS 返回的完整 URL（a.href）
            next_basename = next_page_raw.split("/")[-1].split(".")[0]
            next_chapter_id = next_basename.split("_")[0]
            if next_chapter_id == base_chapter_id:
                next_page_url = next_page_raw
                
        if next_page_url:
            page_url = next_page_url
        else:
            break
            
    content = "\n".join(all_paragraphs).strip() or "[内容获取失败]"
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
