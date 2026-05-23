"""
小说阅读器 Web 版
运行: python web_app.py
浏览器打开: http://localhost:5000
"""

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests as http_requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify

from novel_sources import registry

app = Flask(__name__)
app.secret_key = "novel-reader-secret-key"

BOOKSHELF_FILE = Path(__file__).parent / "bookshelf.json"


# ── 工具 ──────────────────────────────────────────────
def load_bookshelf() -> dict:
    if BOOKSHELF_FILE.exists():
        return json.loads(BOOKSHELF_FILE.read_text("utf-8"))
    return {}


def save_bookshelf(data: dict):
    BOOKSHELF_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")


def _find_shelf_key(shelf: dict, url: str) -> str | None:
    if not url:
        return None
    if url in shelf:
        return url
    url_stripped = url.rstrip('/')
    for key in shelf:
        if key.rstrip('/') == url_stripped:
            return key
    return None


def _get_source(source_id: str=None):
    """获取指定源，不指定则返回默认源"""
    if source_id:
        mod = registry.get(source_id)
        if mod:
            return mod
    return registry.get_default()


def _all_sources():
    """返回模板可用的源列表"""
    return registry.get_all()


# ── 页面路由 ──────────────────────────────────────────
@app.route("/")
def index():
    shelf = load_bookshelf()
    novels = []
    for url, info in shelf.items():
        novels.append({
            "name": info.get("name", "未知"),
            "url": url,
            "source": info.get("source", ""),
            "cover": info.get("cover", ""),
            "last_chapter": info.get("last_chapter", 0),
            "last_title": info.get("last_title", ""),
            "total_chapters": info.get("total_chapters", 0),
            "last_read_time": info.get("last_read_time", 0),
        })
    # 按最后点击/阅读时间从新到旧排序
    novels.sort(key=lambda x: x["last_read_time"], reverse=True)
    return render_template("index.html", novels=novels, sources=_all_sources())


@app.route("/search")
def search():
    keyword = request.args.get("q", "").strip()
    source_id = request.args.get("source", "")
    results = []
    error = None
    if keyword:
        if source_id:
            source = _get_source(source_id)
            if source:
                try:
                    results = source.search(keyword)
                    for r in results:
                        r["source"] = source_id
                        r["source_name"] = getattr(source, "NAME", source_id)
                except Exception as e:
                    error = f"搜索出错: {e}"
        else:
            all_sources = _all_sources()
            errors = []
            
            def fetch_search(sid, sname):
                try:
                    src = _get_source(sid)
                    if src:
                        res = src.search(keyword)
                        for r in res:
                            r["source"] = sid
                            r["source_name"] = sname
                        return res, None
                except Exception as e:
                    return [], f"【{sname}】搜索失败: {e}"
                return [], None
            
            with ThreadPoolExecutor(max_workers=max(1, len(all_sources))) as executor:
                future_to_source = {
                    executor.submit(fetch_search, sid, sname): (sid, sname)
                    for sid, sname in all_sources
                }
                for future in as_completed(future_to_source):
                    sid, sname = future_to_source[future]
                    try:
                        res, err = future.result()
                        if res:
                            results.extend(res)
                        if err:
                            errors.append(err)
                    except Exception as e:
                        errors.append(f"【{sname}】错误: {e}")
            if errors and not results:
                error = " | ".join(errors)

        # 将完全匹配名字的结果放在最前面
        exact = [r for r in results if r.get("name", "").strip().lower() == keyword.lower()]
        others = [r for r in results if r.get("name", "").strip().lower() != keyword.lower()]
        results = exact + others

    return render_template("search.html",
                           keyword=keyword,
                           results=results,
                           error=error,
                           current_source=source_id,
                           sources=_all_sources())


@app.route("/novel/<path:novel_url>")
def novel_detail(novel_url):
    full_url = novel_url
    source_id = request.args.get("source", "")
    source = _get_source(source_id)
    force_refresh = request.args.get("refresh", "") == "1"

    try:
        chapters = source.get_chapters(full_url, force_refresh=force_refresh)
    except Exception as e:
        return render_template("error.html", message=f"获取章节列表失败: {e}"), 500

    shelf = load_bookshelf()
    shelf_key = _find_shelf_key(shelf, full_url) or full_url
    shelf_info = shelf.get(shelf_key, {})
    
    novel_name = shelf_info.get("name")
    cover_url = shelf_info.get("cover")

    # 如果不在书架，或者强制刷新，或者关键信息缺失，才去抓取网页
    if not novel_name or force_refresh or not cover_url:
        novel_name = "未知小说"
        try:
            html = ""
            try:
                resp = http_requests.get(full_url, headers=source.HEADERS, timeout=15)
                if resp.status_code == 200:
                    resp.encoding = "utf-8"
                    # 检查是否为 Cloudflare 等人机挑战页面
                    if any(k in resp.text for k in ("Just a moment", "Checking your browser", "安全检查", "ddos-guard")):
                        raise Exception("Detected Cloudflare/DDOS protection page")
                    html = resp.text
                elif hasattr(source, "fetch_html"):
                    print(f"[web_app] requests detail status {resp.status_code}. Falling back to Playwright...")
                    html = source.fetch_html(full_url)
            except Exception as e:
                if hasattr(source, "fetch_html"):
                    print(f"[web_app] requests detail failed: {e}. Falling back to Playwright...")
                    html = source.fetch_html(full_url)
                else:
                    raise e
            
            if not html:
                raise Exception("无法获取页面内容")

            soup = BeautifulSoup(html, "lxml")
            title_tag = soup.select_one("h1#name, div#info h1, div.info h1, div.book-info h1, h1")
            novel_name = title_tag.get_text(strip=True) if title_tag else "未知小说"
            if len(novel_name) < 3 or novel_name in ("笔趣阁", "首页"):
                page_title = soup.title.get_text() if soup.title else ""
                if "(" in page_title:
                    novel_name = page_title.split("(")[0].strip()
                elif "_" in page_title:
                    novel_name = page_title.split("_")[0].strip()

            # 提取封面图
            cover_url = ""
            for img in soup.select("img"):
                src = img.get("src", "") or img.get("data-src", "")
                if not src:
                    continue
                if src.startswith("//"):
                    src = "https:" + src
                elif src.startswith("/"):
                    src = source.BASE_URL + src
                if src.startswith("http") and any(k in src.lower() for k in ["cover", "image", "photo", "book", ".jpg", ".png", ".webp"]):
                    cover_url = src
                    break
        except Exception:
            if not novel_name:
                novel_name = "未知小说"

    # 保存/更新书架信息
    if shelf_key not in shelf:
        shelf[shelf_key] = {
            "name": novel_name,
            "url": shelf_key,
            "source": source_id,
            "cover": cover_url,
            "last_chapter": 0,
            "last_title": "",
            "total_chapters": len(chapters),
            "last_read_time": time.time(),
        }
        save_bookshelf(shelf)
    else:
        shelf[shelf_key]["total_chapters"] = len(chapters)
        if novel_name and novel_name != "未知小说":
            shelf[shelf_key]["name"] = novel_name
        if cover_url:
            shelf[shelf_key]["cover"] = cover_url
        shelf[shelf_key]["last_read_time"] = time.time()
        save_bookshelf(shelf)

    shelf_info = load_bookshelf().get(shelf_key, {})

    return render_template("novel.html",
                           novel_name=novel_name or "未知小说",
                           novel_url=shelf_key,
                           chapters=chapters,
                           last_chapter=shelf_info.get("last_chapter", 0),
                           source_id=source_id)


@app.route("/read/<path:novel_url>/<int:chapter_idx>")
def read_chapter(novel_url, chapter_idx):
    full_url = novel_url
    source_id = request.args.get("source", "")

    # 从书架中获取之前记录的源
    shelf = load_bookshelf()
    shelf_key = _find_shelf_key(shelf, full_url)
    
    if shelf_key and not source_id:
        source_id = shelf[shelf_key].get("source", "")

    source = _get_source(source_id)

    try:
        chapters = source.get_chapters(full_url)
    except Exception as e:
        return render_template("error.html", message=f"获取章节失败: {e}"), 500

    if chapter_idx < 0 or chapter_idx >= len(chapters):
        return "章节不存在", 404

    ch = chapters[chapter_idx]
    try:
        content = source.get_content(ch["url"])
    except Exception as e:
        return render_template("error.html", message=f"获取内容失败: {e}"), 500

    # 预读后续章节
    if hasattr(source, "prefetch"):
        next_urls = [chapters[i]["url"] for i in range(chapter_idx + 1, min(chapter_idx + 1 + 3, len(chapters)))]
        if next_urls:
            source.prefetch(next_urls)

    # 获取并更新阅读进度
    last_para_idx = 0
    if shelf_key:
        if shelf[shelf_key].get("last_chapter") == chapter_idx:
            last_para_idx = shelf[shelf_key].get("last_para_idx", 0)
        else:
            shelf[shelf_key]["last_para_idx"] = 0

        shelf[shelf_key]["last_chapter"] = chapter_idx
        shelf[shelf_key]["last_title"] = ch["title"]
        shelf[shelf_key]["last_read_time"] = time.time()
        save_bookshelf(shelf)

    novel_name = shelf.get(shelf_key, {}).get("name", "未知小说")

    return render_template("reader.html",
                           novel_name=novel_name,
                           novel_url=shelf_key or full_url,
                           chapter_title=ch["title"],
                           chapter_idx=chapter_idx,
                           total_chapters=len(chapters),
                           content=content,
                           source_id=source_id,
                           last_para_idx=last_para_idx)


@app.route("/api/bookshelf/progress", methods=["POST"])
def api_bookshelf_progress():
    data = request.json
    url = data.get("url")
    chapter_idx = data.get("chapter_idx")
    para_idx = data.get("para_idx", 0)
    chapter_title = data.get("chapter_title", "")

    if not url:
        return jsonify({"error": "缺少 url"}), 400

    shelf = load_bookshelf()
    shelf_key = _find_shelf_key(shelf, url)
    if shelf_key:
        shelf[shelf_key]["last_chapter"] = chapter_idx
        if chapter_title:
            shelf[shelf_key]["last_title"] = chapter_title
        shelf[shelf_key]["last_para_idx"] = para_idx
        shelf[shelf_key]["last_read_time"] = time.time()
        save_bookshelf(shelf)
        return jsonify({"ok": True})
    return jsonify({"error": "书籍不在书架中"}), 404



@app.route("/api/sources")
def api_sources():
    """API: 返回所有可用书源"""
    return jsonify([{"id": sid, "name": name} for sid, name in _all_sources()])


@app.route("/api/bookshelf", methods=["POST"])
def api_bookshelf():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "缺少 url"}), 400

    shelf = load_bookshelf()
    shelf_key = _find_shelf_key(shelf, url) or url
    if shelf_key not in shelf:
        shelf[shelf_key] = {
            "name": data.get("name", "未知"),
            "url": shelf_key,
            "source": data.get("source", ""),
            "last_chapter": 0,
            "last_title": "",
            "total_chapters": data.get("total_chapters", 0),
            "last_read_time": time.time(),
        }
        save_bookshelf(shelf)
    return jsonify({"ok": True})


@app.route("/api/bookshelf/<path:url>", methods=["DELETE"])
def api_delete_bookshelf(url):
    shelf = load_bookshelf()
    shelf_key = _find_shelf_key(shelf, url)
    if shelf_key:
        del shelf[shelf_key]
        save_bookshelf(shelf)
    return jsonify({"ok": True})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    print("\n  小说阅读器已启动")
    print(f"  浏览器打开: http://localhost:{port}\n")
    print(f"  Debug 模式: {'开启' if debug else '关闭（生产模式）'}\n")
    app.run(host="0.0.0.0", port=port, debug=debug)

