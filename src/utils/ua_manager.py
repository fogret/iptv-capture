import re
import json
import os

UA_CACHE_FILE = "data/ua_cache.json"
os.makedirs("data", exist_ok=True)

DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)

# 国内可访问、最通用 Referer
DEFAULT_REFERER = "https://www.baidu.com/"

# 需要 UA 的 CDN / 域名
UA_DOMAINS = [
    "39.134.",     # 央视
    "223.110.",    # 电信
    "183.207.",    # 上海移动
]

# 需要 UA 的格式
UA_FORMATS = [
    ".flv",
    ".f4m",
]

def load_cache():
    if os.path.exists(UA_CACHE_FILE):
        try:
            return json.load(open(UA_CACHE_FILE, "r", encoding="utf-8"))
        except:
            return {}
    return {}

def save_cache(cache):
    json.dump(cache, open(UA_CACHE_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

UA_CACHE = load_cache()


def need_ua(url: str) -> bool:
    if url in UA_CACHE:
        return UA_CACHE[url]

    u = url.lower()

    if any(u.endswith(ext) for ext in UA_FORMATS):
        UA_CACHE[url] = True
        save_cache(UA_CACHE)
        return True

    for d in UA_DOMAINS:
        if d in url:
            UA_CACHE[url] = True
            save_cache(UA_CACHE)
            return True

    UA_CACHE[url] = False
    save_cache(UA_CACHE)
    return False


def get_headers_for_url(url: str) -> dict:
    if need_ua(url):
        return {
            "User-Agent": DEFAULT_UA,
            "Referer": DEFAULT_REFERER,
            "Accept": "*/*",
        }
    return {}


def add_headers_if_needed(url: str) -> str:
    if not url.startswith("http"):
        return url

    if need_ua(url):
        return f"{url}|User-Agent={DEFAULT_UA}&Referer={DEFAULT_REFERER}"

    return url
