"""
统一文件缓存 — 线程安全，带 TTL，重启不丢失
"""

import json
import hashlib
import threading
import time
from pathlib import Path

CACHE_DIR = Path(__file__).parent.parent / "cache"
CONTENT_DIR = CACHE_DIR / "content"
CHAPTERS_DIR = CACHE_DIR / "chapters"
META_FILE = CACHE_DIR / "meta.json"

_lock = threading.Lock()

# TTL（秒）
CONTENT_TTL = 7 * 24 * 3600   # 正文缓存 7 天
CHAPTERS_TTL = 24 * 3600       # 目录缓存 1 天


def _ensure_dirs():
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)


def _key(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def _read_json(path: Path):
    try:
        data = json.loads(path.read_text("utf-8"))
        if time.time() - data.get("ts", 0) < data.get("ttl", 0):
            return data.get("value")
    except Exception:
        pass
    return None


def _write_json(path: Path, value, ttl: int):
    try:
        path.write_text(json.dumps({
            "ts": time.time(),
            "ttl": ttl,
            "value": value,
        }, ensure_ascii=False), "utf-8")
    except Exception:
        pass


# ── 正文缓存 ──────────────────────────────────────────
def get_content(url: str) -> str | None:
    _ensure_dirs()
    with _lock:
        return _read_json(CONTENT_DIR / f"{_key(url)}.json")


def set_content(url: str, text: str, ttl: int = CONTENT_TTL):
    _ensure_dirs()
    with _lock:
        _write_json(CONTENT_DIR / f"{_key(url)}.json", text, ttl)


# ── 目录缓存 ──────────────────────────────────────────
def get_chapters(url: str) -> list | None:
    _ensure_dirs()
    with _lock:
        return _read_json(CHAPTERS_DIR / f"{_key(url)}.json")


def set_chapters(url: str, chapters: list, ttl: int = CHAPTERS_TTL):
    _ensure_dirs()
    with _lock:
        _write_json(CHAPTERS_DIR / f"{_key(url)}.json", chapters, ttl)


# ── 通用 KV（用于 cookie 等）──────────────────────────
def get_meta(key: str):
    _ensure_dirs()
    with _lock:
        try:
            data = json.loads(META_FILE.read_text("utf-8"))
            entry = data.get(key)
            if entry and time.time() - entry.get("ts", 0) < entry.get("ttl", 0):
                return entry.get("value")
        except Exception:
            pass
    return None


def set_meta(key: str, value, ttl: int = 3600):
    _ensure_dirs()
    with _lock:
        try:
            data = json.loads(META_FILE.read_text("utf-8"))
        except Exception:
            data = {}
        data[key] = {"ts": time.time(), "ttl": ttl, "value": value}
        META_FILE.write_text(json.dumps(data, ensure_ascii=False), "utf-8")


# ── 清理 ──────────────────────────────────────────────
def clear_all():
    import shutil
    with _lock:
        if CACHE_DIR.exists():
            shutil.rmtree(CACHE_DIR)
