"""
全局共享 Playwright 并发池 — 所有书源复用同一个浏览器实例

设计要点：
- async Playwright 运行在独立的事件循环线程中
- 单一 browser + context，asyncio.Semaphore 控制并发 page 数
- 相比各书源独立 browser，节省约 150MB+ 内存
- 支持多章预读并发，不再串行排队
- 所有公共接口均为同步方法，可从任意线程调用
"""

import asyncio
import threading

PLAYWRIGHT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)

_pool_instance = None
_pool_lock = threading.Lock()


def get_pool() -> "PlaywrightPool":
    """获取全局共享的 Playwright 池（懒加载单例）"""
    global _pool_instance
    if _pool_instance is None:
        with _pool_lock:
            if _pool_instance is None:
                _pool_instance = PlaywrightPool(max_concurrent=3)
    return _pool_instance


class PlaywrightPool:
    """
    基于 async Playwright 的并发页面池。
    所有书源共享同一个 browser + context，通过 asyncio.Semaphore 控制并发 page 数上限。
    调用方无需关心异步/线程，所有方法以同步阻塞方式返回结果。
    """

    def __init__(self, max_concurrent: int = 3, headless: bool = True):
        self._max_concurrent = max_concurrent
        self._headless = headless
        self._loop = None
        self._browser = None
        self._context = None
        self._semaphore = None
        self._ready = threading.Event()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        if not self._ready.wait(timeout=30):
            raise RuntimeError("[PlaywrightPool] 启动超时，请检查 Playwright 浏览器是否已安装")

    # ── 事件循环线程 ──────────────────────────────────────

    def _run_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._loop = loop
        try:
            loop.run_until_complete(self._async_init())
        except Exception as e:
            print(f"[PlaywrightPool] 初始化失败: {e}")
            self._init_error = e
        finally:
            self._ready.set()  # 无论成功失败都要释放，避免调用方永久阻塞
        loop.run_forever()

    async def _async_init(self):
        import os
        from playwright.async_api import async_playwright
        pw = await async_playwright().start()

        # 自动判定无头模式：
        # 1. 优先读取环境变量 PLAYWRIGHT_HEADLESS (如 "true", "false")
        # 2. 如果是 Linux 且无图形界面 ($DISPLAY 未设置)，强制设为 True，防止启动失败
        headless_env = os.environ.get("PLAYWRIGHT_HEADLESS")
        if headless_env is not None:
            headless = headless_env.lower() in ("1", "true", "yes")
        else:
            if os.name != "nt" and not os.environ.get("DISPLAY"):
                headless = True
            else:
                headless = self._headless

        self._browser = await pw.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--window-position=-32000,-32000",
                "--window-size=10,10",
            ],
        )
        self._context = await self._browser.new_context(
            user_agent=PLAYWRIGHT_USER_AGENT,
            viewport={"width": 1024, "height": 768},
        )
        await self._context.add_init_script(
            'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
        )
        self._semaphore = asyncio.Semaphore(self._max_concurrent)
        print(f"[PlaywrightPool] 浏览器池已就绪（最大并发页面数: {self._max_concurrent}）")

    # ── 提交机制 ──────────────────────────────────────────

    def _submit(self, coro, timeout: float = 90):
        """将协程提交到后台事件循环，阻塞等待结果（最长 timeout 秒）"""
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=timeout)

    # ── 内部异步实现 ──────────────────────────────────────

    async def _async_open_page(self, url: str, wait_fn: str | None, wait_timeout: int):
        """打开页面，可选等待 JS 条件，返回 page（调用方负责关闭）"""
        page = await self._context.new_page()
        await page.goto(url, timeout=30000)
        if wait_fn:
            try:
                await page.wait_for_function(wait_fn, timeout=wait_timeout)
            except Exception as e:
                print(f"[PlaywrightPool] wait_for_function 超时/错误 ({url}): {e}")
        return page

    async def _async_fetch_html(self, url: str, wait_fn: str | None, wait_timeout: int) -> str:
        async with self._semaphore:
            page = await self._async_open_page(url, wait_fn, wait_timeout)
            try:
                return await page.content()
            finally:
                await page.close()

    async def _async_fetch_evaluate(self, url: str, js_code: str,
                                    wait_fn: str | None, wait_timeout: int):
        async with self._semaphore:
            page = await self._async_open_page(url, wait_fn, wait_timeout)
            try:
                return await page.evaluate(js_code)
            finally:
                await page.close()

    async def _async_get_cookies(self) -> list:
        return await self._context.cookies()

    # ── 公共同步接口（可从任意线程调用）────────────────────

    def fetch_html(self, url: str, wait_fn: str = None, wait_timeout: int = 8000) -> str:
        """
        获取页面完整 HTML（带信号量并发控制）。
        wait_fn: 可选 JS 布尔表达式字符串，等待其返回 true 后再获取 HTML。
        """
        return self._submit(self._async_fetch_html(url, wait_fn, wait_timeout))

    def fetch_evaluate(self, url: str, js_code: str,
                       wait_fn: str = None, wait_timeout: int = 8000):
        """
        在页面中执行 JS 并返回结果（适合提取结构化数据）。
        js_code: 合法的 JS 函数表达式字符串，如 '() => document.title'
        """
        return self._submit(self._async_fetch_evaluate(url, js_code, wait_fn, wait_timeout))

    def get_cookies(self) -> list:
        """获取当前 context 中所有域的 cookie 列表"""
        return self._submit(self._async_get_cookies())
