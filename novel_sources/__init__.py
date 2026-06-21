import time
import urllib3
import requests

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
