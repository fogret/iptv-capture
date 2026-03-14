import os
import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from utils.logger import logger
from utils.stats import stats
from utils.ua_manager import get_headers_for_url   # ⭐ 接入智能 UA

# 路径保持不变（你要求的）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCES_DIR = os.path.join(BASE_DIR, "sources")

MAX_PAGES = 100
MAX_DEPTH = 3
MAX_CHANNELS = 200

AD_KEYWORDS = ["ad", "ads", "advert", "banner", "promo", "doubleclick", "googleads"]


def is_ad_url(url: str) -> bool:
    url_lower = url.lower()
    return any(k in url_lower for k in AD_KEYWORDS)


# ================================
# ⭐ 接入智能 UA 的网页抓取
# ================================
def fetch_html(url: str) -> str:
    try:
        headers = get_headers_for_url(url, mode="play")  # ⭐ 自动 UA / Referer / Cookie / Host
        resp = requests.get(url, headers=headers, timeout=8)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        return resp.text
    except Exception as e:
        logger.warning(f"[websites] 抓取失败: {url} ({e})")
        return ""


# ================================
# ⭐ 全格式直播流提取器（完整版）
# ================================
def extract_streams(html: str, base_url: str) -> list:
    urls = set()
    soup = BeautifulSoup(html, "html.parser")

    # 1) video 标签
    for video in soup.find_all("video"):
        src = video.get("src")
        if src:
            urls.add(urljoin(base_url, src))

    # 2) 常见直播格式
    patterns = [
        r'https?://[^\s"\']+?\.m3u8[^\s"\']*',
        r'https?://[^\s"\']+?\.flv[^\s"\']*',
        r'https?://[^\s"\']+?\.ts[^\s"\']*',
        r'https?://[^\s"\']+?\.mp4[^\s"\']*',
        r'https?://[^\s"\']+?\.mpd[^\s"\']*',
        r'https?://[^\s"\']+?\.f4m[^\s"\']*',
        r'rtmp://[^\s"\']+',
        r'https?://[^\s"\']+?live[^\s"\']*',
    ]

    for p in patterns:
        for m in re.findall(p, html, flags=re.IGNORECASE):
            urls.add(urljoin(base_url, m))

    # 3) JS 播放器配置（DPlayer / CKPlayer / xgplayer / video.js）
    js_patterns = [
        r'url\s*[:=]\s*["\']([^"\']+)',
        r'src\s*[:=]\s*["\']([^"\']+)',
        r'file\s*[:=]\s*["\']([^"\']+)',
        r'playurl\s*[:=]\s*["\']([^"\']+)',
    ]

    for p in js_patterns:
        for m in re.findall(p, html, flags=re.IGNORECASE):
            if m.startswith("http") or m.startswith("rtmp"):
                urls.add(urljoin(base_url, m))

    # 4) iframe 递归抓取
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src")
        if not src:
            continue

        iframe_url = urljoin(base_url, src)
        sub_html = fetch_html(iframe_url)
        if sub_html:
            sub_streams = extract_streams(sub_html, iframe_url)
            for s in sub_streams:
                urls.add(s)

    # 5) HLS 深度解析（子 m3u8 + KEY + TS）
    m3u8_list = [u for u in urls if u.endswith(".m3u8")]

    for m3u8_url in m3u8_list:
        try:
            text = fetch_html(m3u8_url)
            if not text:
                continue

            for line in text.splitlines():
                line = line.strip()

                # 子 m3u8
                if line.endswith(".m3u8") and not line.startswith("#"):
                    urls.add(urljoin(m3u8_url, line))

                # TS
                if line.endswith(".ts"):
                    urls.add(urljoin(m3u8_url, line))

                # KEY
                if line.startswith("#EXT-X-KEY"):
                    m = re.search(r'URI="([^"]+)"', line)
                    if m:
                        urls.add(urljoin(m3u8_url, m.group(1)))

        except:
            pass

    return list(urls)


def extract_links(html: str, base_url: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("#"):
            continue
        full = urljoin(base_url, href)
        if not is_ad_url(full):
            links.append(full)

    return links


def guess_channel_name(url: str, html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
        if 0 < len(title) <= 20:
            return title

    m = re.search(r"(cctv\d+|hunantv|gzstv|channel\d+)", url.lower())
    if m:
        return m.group(1).upper()

    return "未知频道"


def guess_group(url: str) -> str:
    u = url.lower()
    if "cctv" in u:
        return "央视"
    if "tv" in u and "cctv" not in u:
        return "卫视"
    if "st" in u or "media" in u or "news" in u:
        return "地方台"
    return "其它"


def collect_from_page(url: str, depth: int, visited: set, channels: list, root_url: str):
    if depth > MAX_DEPTH or len(visited) > MAX_PAGES or len(channels) > MAX_CHANNELS:
        return

    if url in visited:
        return
    visited.add(url)

    logger.info(f"[websites] 抓取页面: {url} (深度 {depth})")

    html = fetch_html(url)
    if not html:
        return

    stats.website_pages_total += 1
    detail = stats.website_detail[root_url]
    detail["pages"] += 1
    if depth > detail["max_depth"]:
        detail["max_depth"] = depth
    if depth > stats.website_max_depth_global:
        stats.website_max_depth_global = depth

    # ⭐ 使用全格式提取器
    streams = extract_streams(html, url)

    if streams:
        logger.info(f"[websites] 页面 {url} 发现 {len(streams)} 个直播流")

        for stream in streams:
            if is_ad_url(stream):
                logger.warning(f"[websites] 屏蔽广告源: {stream}")
                detail["ads_blocked"].append(stream)
                stats.website_ads_blocked_total += 1
                continue

            name = guess_channel_name(url, html)
            group = guess_group(url)

            ch = {
                "name": name,
                "group": group,
                "url": stream,
                "origin": "website",
                "root_site": root_url,
            }
            channels.append(ch)
            detail["channels"].append({"name": name, "url": stream})

        return

    # 递归子页面
    links = extract_links(html, url)
    for link in links:
        logger.info(f"[websites] 递归进入子页面: {link}")
        collect_from_page(link, depth + 1, visited, channels, root_url)


def collect_websites():
    channels = []

    if not os.path.exists(SOURCES_DIR):
        logger.warning(f"[websites] sources 目录不存在: {SOURCES_DIR}")
        return channels

    for file in os.listdir(SOURCES_DIR):
        if not file.endswith(".txt"):
            continue

        path = os.path.join(SOURCES_DIR, file)
        if os.path.getsize(path) == 0:
            continue

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                url = line.strip()
                if not url or url.startswith("#"):
                    continue
                if not url.startswith("http"):
                    continue

                if url not in stats.website_detail:
                    stats.website_detail[url] = {
                        "pages": 0,
                        "max_depth": 0,
                        "channels": [],
                        "ads_blocked": [],
                    }

                visited = set()
                collect_from_page(url, 1, visited, channels, root_url=url)

    logger.info(f"[websites] 网站抓取共得到 {len(channels)} 条频道")
    return channels
