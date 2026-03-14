import re
import json
import os
import aiohttp
import asyncio

UA_CACHE_FILE = "data/ua_cache.json"
os.makedirs("data", exist_ok=True)

# ===========================
# 1) 默认 UA（国内环境）
# ===========================
DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)

DEFAULT_REFERER = "https://www.baidu.com/"

# ===========================
# 2) 播放器 UA
# ===========================
PLAYER_UA = {
    "tvbox": DEFAULT_UA,
    "potplayer": "Lavf/58.45.100",
    "vlc": "VLC/3.0.18",
    "android": "Mozilla/5.0 (Linux; Android 10)",
}

# ===========================
# 3) CDN 规则（是否需要 UA）
# ===========================
CDN_RULES = {
    "39.134.": True,   # 央视
    "223.110.": True,  # 电信
    "183.207.": True,  # 移动
    "101.71.": False,  # 阿里 CDN
    "112.50.": False,  # 腾讯 CDN
}

# ===========================
# 4) Referer 规则（按域名）
# ===========================
REFERER_RULES = {
    "cctv.cn": "https://www.cctv.cn/",
    "cntv.cn": "https://www.cntv.cn/",
    "mgtv.com": "https://www.mgtv.com/",
    "iqiyi.com": "https://www.iqiyi.com/",
    "youku.com": "https://www.youku.com/",
    "iptv.gz.cn": "https://iptv.gz.cn/",
}

# ===========================
# 5) Cookie 规则（按域名）
# ===========================
COOKIE_RULES = {
    "iptv.gz.cn": "sessionid=123456;",
}

# ===========================
# 6) Host 规则（按 CDN）
# ===========================
HOST_RULES = {
    "39.134.": "live.cctv.com",
    "223.110.": "live.telecom.com",
}

# ===========================
# 7) 格式规则（需要 UA）
# ===========================
FORMAT_RULES = [
    ".flv",
    ".f4m",
]

# ===========================
# 8) EPG UA 规则
# ===========================
EPG_RULES = {
    "epg.51zmt.top": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "epg.pw": "Mozilla/5.0 (Linux; Android 10)",
    "xmltv.se": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
}

# ===========================
# 9) 截图 UA
# ===========================
SCREENSHOT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# ===========================
# 10) 缓存
# ===========================
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

# ===========================
# 11) 判断是否需要 UA
# ===========================
def need_ua(url: str) -> bool:
    if url in UA_CACHE:
        return UA_CACHE[url]

    u = url.lower()

    # 按格式
    if any(u.endswith(ext) for ext in FORMAT_RULES):
        UA_CACHE[url] = True
        save_cache(UA_CACHE)
        return True

    # 按 CDN
    for prefix, need in CDN_RULES.items():
        if prefix in url:
            UA_CACHE[url] = need
            save_cache(UA_CACHE)
            return need

    UA_CACHE[url] = False
    save_cache(UA_CACHE)
    return False

# ===========================
# 12) 自动识别网页中的真实 UA
# ===========================
def extract_real_ua(html: str):
    m = re.search(r'User-Agent["\']?\s*[:=]\s*["\']([^"\']+)', html)
    if m:
        return m.group(1)
    return None

# ===========================
# 13) 获取 Referer
# ===========================
def get_referer(url: str) -> str:
    for domain, ref in REFERER_RULES.items():
        if domain in url:
            return ref
    return DEFAULT_REFERER

# ===========================
# 14) 获取 Cookie
# ===========================
def get_cookie(url: str) -> str:
    for domain, ck in COOKIE_RULES.items():
        if domain in url:
            return ck
    return ""

# ===========================
# 15) 获取 Host
# ===========================
def get_host(url: str) -> str:
    for prefix, host in HOST_RULES.items():
        if prefix in url:
            return host
    return ""

# ===========================
# 16) 获取 headers（检测/测速/截图/EPG）
# ===========================
def get_headers_for_url(url: str, mode="play", player="tvbox") -> dict:
    # EPG 模式
    if mode == "epg":
        for domain, ua in EPG_RULES.items():
            if domain in url:
                return {"User-Agent": ua}

    # 截图模式
    if mode == "screenshot":
        return {"User-Agent": SCREENSHOT_UA}

    # 播放/检测模式
    if not need_ua(url):
        return {}

    ua = PLAYER_UA.get(player, DEFAULT_UA)
    referer = get_referer(url)
    cookie = get_cookie(url)
    host = get_host(url)

    headers = {
        "User-Agent": ua,
        "Referer": referer,
        "Accept": "*/*",
    }

    if cookie:
        headers["Cookie"] = cookie

    if host:
        headers["Host"] = host
        headers["Origin"] = f"https://{host}"

    return headers

# ===========================
# 17) 导出 URL（M3U / TVBox）
# ===========================
def add_headers_if_needed(url: str, player="tvbox") -> str:
    if not url.startswith("http"):
        return url

    if not need_ua(url):
        return url

    ua = PLAYER_UA.get(player, DEFAULT_UA)
    referer = get_referer(url)

    return f"{url}|User-Agent={ua}&Referer={referer}"

# ===========================
# 18) fallback（失败 → 自动加 UA）
# ===========================
async def test_url(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=2) as resp:
                return resp.status < 500
    except:
        return False

async def fallback_ua(url):
    ok = await test_url(url)
    if ok:
        UA_CACHE[url] = False
        save_cache(UA_CACHE)
        return False

    UA_CACHE[url] = True
    save_cache(UA_CACHE)
    return True
