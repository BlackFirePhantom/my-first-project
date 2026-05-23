"""
哔哩轻小说源 (www.linovelib.com)
直接 requests 抓取目录/搜索，使用共享 Playwright 池 (playwright_base) 获取正文以绕过内容截断与加密限制。
"""

import re
import threading
from concurrent.futures import ThreadPoolExecutor
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

# Cloudflare 等待条件
_CF_WAIT_FN = r"""
() => {
    const t = document.title;
    if (t.includes('Just a moment') || t.includes('Checking your browser') || t.includes('Attention Required')) {
        return false;
    }
    return document.body && document.body.innerText.length > 100;
}
"""

# ── Playwright JS 常量 ────────────────────────────────
# 等待函数：检测混淆样式表是否已将 display:none / scale(0) / absolute 注入
_WAIT_FN = r"""
() => {
    const el = document.querySelector('div#mlfy_main_text');
    if (!el || !el.innerText) return false;
    const text = el.innerText;
    if (text.includes('内容加载失败') || text.includes('內容加載失敗') ||
        text.includes('数据缺失') || text.includes('正在加载')) {
        return false;
    }
    for (let i = 0; i < document.styleSheets.length; i++) {
        try {
            const sheet = document.styleSheets[i];
            const rules = sheet.cssRules || sheet.rules;
            if (!rules) continue;
            for (let j = 0; j < rules.length; j++) {
                const rule = rules[j];
                if (rule.cssText &&
                    (rule.cssText.includes('display: none') ||
                     rule.cssText.includes('scale(0)') ||
                     rule.cssText.includes('absolute')) &&
                    rule.selectorText && rule.selectorText.includes('TextContent')) {
                    return true;
                }
            }
        } catch (e) {}
    }
    return false;
}
"""

# 提取章节数据的 JS：移除注音/干扰标签，过滤隐藏段落，获取下一页链接
_CHAPTER_JS = r"""
() => {
    const container = document.querySelector('#TextContent');
    if (!container) return { paragraphs: [], nextPage: null };

    // 移除注音和无用干扰标签
    container.querySelectorAll('rt').forEach(rt => rt.remove());
    container.querySelectorAll('.dag').forEach(dag => dag.remove());

    const pTags = Array.from(container.querySelectorAll('p'));
    const paragraphs = [];
    if (pTags.length > 0) {
        pTags.forEach(p => {
            const style = window.getComputedStyle(p);
            const isHidden = style.display === 'none' ||
                             style.position === 'absolute' ||
                             style.transform.includes('matrix(0');
            if (!isHidden) {
                const text = p.innerText.trim();
                if (text) paragraphs.push(text);
            }
        });
    } else {
        const text = container.innerText.trim();
        if (text) {
            paragraphs.push(...text.split('\n').map(s => s.trim()).filter(s => s));
        }
    }

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
    return { paragraphs, nextPage };
}
"""


def fetch_html(url: str) -> str:
    """获取整页 HTML（使用共享 Playwright 池绕过 Cloudflare）"""
    from novel_sources import playwright_base
    return playwright_base.get_pool().fetch_html(url, wait_fn=_CF_WAIT_FN, wait_timeout=15000)


def _fetch_chapter_data(url: str) -> dict:
    """
    在 Playwright 浏览器中直接通过 JS evaluate() 提取章节数据。
    使用共享池并发执行，不再串行排队。
    返回: {"paragraphs": list[str], "nextPage": str or None}
    """
    from novel_sources import playwright_base
    result = playwright_base.get_pool().fetch_evaluate(
        url, _CHAPTER_JS, wait_fn=_WAIT_FN, wait_timeout=8000
    )
    return result if result else {"paragraphs": [], "nextPage": None}


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
            try:
                resp = robust_get(target_url, headers=HEADERS, timeout=15)
                if resp.status_code != 200:
                    raise Exception(f"HTTP status code {resp.status_code}")
                # 检查是否为 Cloudflare 等人机挑战页面
                if any(k in resp.text for k in ("Just a moment", "Checking your browser", "安全检查", "ddos-guard")):
                    raise Exception("Detected Cloudflare/DDOS protection page")
                html = resp.text
            except Exception as e:
                print(f"[linovelib] requests get detail failed: {e}. Falling back to Playwright...")
                html = fetch_html(target_url)
            
            soup = BeautifulSoup(html, "lxml")
            
            # 使用 og 标签提取，最准确且不受改版影响
            title_meta = soup.find("meta", property="og:title")
            author_meta = soup.find("meta", property="og:novel:author") or soup.find("meta", attrs={"name": "author"})
            
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


def _is_cf_blocked(html: str) -> bool:
    """判断 HTML 是否是 Cloudflare 拦截页（Just a moment / 挑战页）"""
    cf_keywords = ("Just a moment", "Checking your browser", "Attention Required",
                   "安全检查", "ddos-guard", "cf-browser-verification")
    return any(k in html for k in cf_keywords)


def _make_catalog_candidates(novel_url: str) -> list[tuple[str, dict]]:
    """
    生成候选目录 URL 列表（含对应的请求头）。
    Azure 云服务器 IP 常被 Cloudflare 拦截，故按顺序尝试：
      1. 原始 www.linovelib.com
      2. 手机版 w.linovelib.com（CF 防护较轻）
      3. 镜像站 www.bilinovel.com（独立 CDN）
    """
    # 构造原始目录 URL
    if "/catalog" in novel_url:
        base_catalog = novel_url
    elif novel_url.endswith(".html"):
        base_catalog = novel_url.replace(".html", "/catalog")
    else:
        base_catalog = novel_url.rstrip("/") + "/catalog"

    candidates = []
    # 1. 原始域
    candidates.append((base_catalog, {**HEADERS, "Referer": BASE_URL}))
    # 2. 手机版（仅对 linovelib.com 适用）
    if "linovelib.com" in base_catalog:
        wap_url = base_catalog.replace("www.linovelib.com", "w.linovelib.com")
        candidates.append((wap_url, {**HEADERS,
                                      "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 "
                                                    "(KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
                                      "Referer": "https://w.linovelib.com/"}))
        bili_url = base_catalog.replace("www.linovelib.com", "www.bilinovel.com")
        candidates.append((bili_url, {**HEADERS, "Referer": "https://www.bilinovel.com/"}))
    return candidates


def _fetch_catalog_html(url: str, headers: dict) -> str:
    """
    尝试用 curl_cffi 获取目录 HTML（模拟 Chrome TLS 指纹绕过 Cloudflare）。
    失败时回退到 Playwright。
    """
    # ── 方法一：curl_cffi（模拟真实 Chrome TLS 指纹）────────────────
    try:
        from curl_cffi import requests as cf_requests
        print(f"[linovelib] curl_cffi 请求: {url}")
        resp = cf_requests.get(url, headers=headers, impersonate="chrome124", timeout=20)
        print(f"[linovelib] curl_cffi 状态码: {resp.status_code}, 长度: {len(resp.text)}")
        if resp.status_code == 200 and not _is_cf_blocked(resp.text):
            return resp.text
        print(f"[linovelib] curl_cffi 失败 (状态码={resp.status_code} 或 CF 拦截)")
    except ImportError:
        print("[linovelib] curl_cffi 未安装，跳过")
    except Exception as e:
        print(f"[linovelib] curl_cffi 异常: {e}")

    # ── 方法二：Playwright（无头浏览器）───────────────────────────────
    print(f"[linovelib] 使用 Playwright 重试: {url}")
    candidate_html = fetch_html(url)
    import re as _re
    title_match = _re.search(r'<title>([^<]+)</title>', candidate_html)
    page_title = title_match.group(1).strip() if title_match else "无"
    print(f"[linovelib] Playwright 页面标题: {page_title}, 长度: {len(candidate_html)}")
    if _is_cf_blocked(candidate_html):
        raise Exception(f"Playwright CF block (title={page_title})")
    return candidate_html


def get_chapters(novel_url: str, force_refresh: bool = False) -> list[dict]:
    """获取小说所有章节目录（curl_cffi TLS 指纹 + 多镜像 + Playwright 三重绕过）"""
    if not force_refresh:
        cached = cache.get_chapters(novel_url)
        if cached:  # 只有非空缓存才使用，空列表视为无效缓存
            return cached

    candidates = _make_catalog_candidates(novel_url)
    html = None
    used_url = None
    last_error = "未知错误"

    for try_url, try_headers in candidates:
        print(f"[linovelib] 尝试获取目录: {try_url}")
        try:
            html = _fetch_catalog_html(try_url, try_headers)
            used_url = try_url
            break
        except Exception as e:
            last_error = str(e)
            print(f"[linovelib] {try_url} 全部方法失败: {e}，尝试下一个镜像...")

    if not html:
        raise Exception(f"所有镜像均无法获取目录，请稍后重试。最后错误: {last_error}")

    print(f"[linovelib] 成功获取目录来源: {used_url}")
    soup = BeautifulSoup(html, "lxml")

    # 提取小说名称，以便用于去除卷标题中的小说名
    novel_name_meta = soup.find("meta", property="og:novel:book_name")
    novel_name = novel_name_meta["content"] if novel_name_meta else None

    chapters = []

    # 遍历每个卷 volume 容器
    volumes = soup.select(".volume-list > .volume")
    print(f"[linovelib] 找到 {len(volumes)} 个卷")
    if not volumes:
        # Fallback: 如果没有 .volume 结构，直接找所有的 a
        seen = set()
        for a in soup.select("ul.chapter-list li a, li.col-4 a, a"):
            href = a.get("href", "")
            text = a.get_text(strip=True)
            if href and text and "/novel/" in href and ".html" in href and "vol_" not in href:
                full_url = urljoin(used_url, href)
                # 将镜像域名统一回 www.linovelib.com，保证正文可正常获取
                full_url = full_url.replace("w.linovelib.com", "www.linovelib.com") \
                                   .replace("www.bilinovel.com", "www.linovelib.com")
                if full_url not in seen:
                    seen.add(full_url)
                    chapters.append({"title": text, "url": full_url})
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
                    full_url = urljoin(used_url, href)
                    # 将镜像域名统一回 www.linovelib.com
                    full_url = full_url.replace("w.linovelib.com", "www.linovelib.com") \
                                       .replace("www.bilinovel.com", "www.linovelib.com")
                    title = f"[{vol_title}] {text}" if vol_title else text
                    chapters.append({"title": title, "url": full_url})

    if chapters:
        print(f"[linovelib] 共获取到 {len(chapters)} 个章节，写入缓存")
        cache.set_chapters(novel_url, chapters)
    else:
        print(f"[linovelib] 警告: 获取到空章节列表，不写入缓存，下次将重新获取")
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
        # 使用新的 chapter 模式：在浏览器 JS 中直接获取过滤后的可见段落和 nextPage
        data = _fetch_chapter_data(page_url)
        page_paragraphs = data.get("paragraphs", [])
        next_page_raw = data.get("nextPage", None)
        
        if not page_paragraphs:
            break
        
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
    """后台并发预读后续章节（利用共享池的多页并发能力）"""
    def _do_prefetch():
        # 过滤掉已缓存的章节，只预读缺失的
        urls_to_fetch = [u for u in chapter_urls if not cache.get_content(u)]
        if not urls_to_fetch:
            return
        with ThreadPoolExecutor(max_workers=len(urls_to_fetch)) as executor:
            futures = [executor.submit(get_content, url) for url in urls_to_fetch]
            for f in futures:
                try:
                    f.result()
                except Exception:
                    pass

    threading.Thread(target=_do_prefetch, daemon=True).start()
