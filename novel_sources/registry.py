"""
书源注册中心 — 自动发现 novel_sources/ 下的所有书源
"""

import importlib
import pkgutil
from pathlib import Path

# 源名 -> 模块对象
_sources: dict = {}
# 有序的源列表 [(id, display_name), ...]
_source_list: list = []


def _discover():
    """扫描 novel_sources 包，加载所有包含 search/get_chapters/get_content 的模块"""
    if _sources:
        return

    package_dir = Path(__file__).parent
    package_name = __package__

    for finder, module_name, is_pkg in pkgutil.iter_modules([str(package_dir)]):
        if module_name.startswith("_") or module_name in ("registry", "base"):
            continue
        try:
            mod = importlib.import_module(f"{package_name}.{module_name}")
        except Exception:
            continue

        # 检查是否实现了必要接口
        if all(hasattr(mod, fn) for fn in ("search", "get_chapters", "get_content")):
            display_name = getattr(mod, "NAME", module_name)
            _sources[module_name] = mod
            _source_list.append((module_name, display_name))

    # 按模块名按字母顺序排序，确保在所有平台上的默认源一致
    _source_list.sort(key=lambda x: x[0])


def get_all() -> list[tuple[str, str]]:
    """返回所有可用源 [(id, display_name), ...]"""
    _discover()
    return list(_source_list)


def get(source_id: str):
    """根据 id 获取源模块"""
    _discover()
    return _sources.get(source_id)


def get_default():
    """获取默认源（第一个）"""
    _discover()
    if _source_list:
        return _sources[_source_list[0][0]]
    return None


def get_by_url(url: str):
    """根据 URL 域名匹配对应的源模块"""
    _discover()
    if not url:
        return None
    from urllib.parse import urlparse
    try:
        url_domain = urlparse(url).netloc.lower()
    except Exception:
        return None
    for source_id, mod in _sources.items():
        base_url = getattr(mod, "BASE_URL", "")
        if base_url:
            try:
                mod_domain = urlparse(base_url).netloc.lower()
                if mod_domain and (mod_domain in url_domain or url_domain in mod_domain):
                    return mod
            except Exception:
                continue
    return None


def get_id_by_url(url: str) -> str | None:
    """根据 URL 域名获取匹配的源 ID"""
    _discover()
    mod = get_by_url(url)
    if mod:
        for sid, m in _sources.items():
            if m == mod:
                return sid
    return None

