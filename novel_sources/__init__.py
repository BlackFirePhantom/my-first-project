import time
import threading
import urllib3
import requests
from concurrent.futures import ThreadPoolExecutor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 共享请求配置
DEFAULT_TIMEOUT = 10
MAX_RETRIES = 2
RETRY_DELAY = 1


def robust_get(url: str, headers: dict = None, timeout: int = DEFAULT_TIMEOUT,
               retries: int = MAX_RETRIES, **kwargs) -> requests.Response:
    """带重试的 GET 请求"""
    kwargs.setdefault("verify", False)
    kwargs.setdefault("timeout", timeout)

    last_err = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, **kwargs)
            resp.encoding = "utf-8"
            return resp
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
    raise last_err


def robust_post(url: str, headers: dict = None, timeout: int = DEFAULT_TIMEOUT,
                retries: int = MAX_RETRIES, **kwargs) -> requests.Response:
    """带重试的 POST 请求"""
    kwargs.setdefault("verify", False)
    kwargs.setdefault("timeout", timeout)

    last_err = None
    for attempt in range(retries):
        try:
            resp = requests.post(url, headers=headers, **kwargs)
            resp.encoding = "utf-8"
            return resp
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
    raise last_err


# ── 并发预读 ──────────────────────────────────────────
def prefetch_concurrent(fetch_fn, chapter_urls: list[str], max_workers: int = 3):
    """
    后台并发预读后续章节（所有书源共用），替代各源原先的串行循环。

    - 命中文件缓存的章节会立即返回，不产生网络请求
    - cache.py 已线程安全；requests / BeautifulSoup 各自独立调用，无共享可变状态
    - 单个章节失败不影响其它章节

    fetch_fn:     源模块的 get_content
    chapter_urls: 待预读的章节 URL 列表
    max_workers:  并发上限（实际取 min(max_workers, len(chapter_urls))）
    """
    if not chapter_urls:
        return

    def _do_prefetch():
        workers = max(1, min(max_workers, len(chapter_urls)))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(fetch_fn, url) for url in chapter_urls]
            for fut in futures:
                try:
                    fut.result()
                except Exception:
                    pass

    threading.Thread(target=_do_prefetch, daemon=True).start()
