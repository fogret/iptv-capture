import os
import re
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from utils.logger import logger
from utils.stats import stats

# 统一路径（与 universal_sources 完全一致）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCES_DIR = os.path.join(BASE_DIR, "sources")

MAX_PAGES = 100
MAX_DEPTH = 3
MAX_CHANNELS = 200

AD_KEYWORDS = ["ad", "ads", "advert", "banner", "promo", "doubleclick", "googleads"]


def is_ad_url(url: str) -> bool:
    url_lower = url.lower()
    return any(k in url_lower for k in AD_KEYWORDS)


def fetch_html(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=8)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        return resp.text
    except Exception as e:
        logger.warning(f"[websites] 抓取失败: {url} ({e})")
        return ""


def extract_m3u8(html: str) -> list:
    urls = set()
    soup = BeautifulSoup(html, "html.parser")

    for video in soup.find_all("video"):
        src = video.get("src")
        if src and src.endswith(".m3u8"):
            urls.add(src)

    matches = re.findall(r'["\'](https?://[^"\']+\.m3u8)["\']', html)
    urls.update(matches)

    matches = re.findall(r'(https?://[^"\']+\.m3u8)', html)
    urls.update(matches)

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

    m3u8_list = extract_m3u8(html)

    if m3u8_list:
        logger.info(f"[websites] 页面 {url} 发现 {len(m3u8_list)} 个 m3u8")

        for m3u8 in m3u8_list:
            if is_ad_url(m3u8):
                logger.warning(f"[websites] 屏蔽广告源: {m3u8}")
                detail["ads_blocked"].append(m3u8)
                stats.website_ads_blocked_total += 1
                continue

            name = guess_channel_name(url, html)
            group = guess_group(url)

            ch = {
                "name": name,
                "group": group,
                "url": m3u8,
                "origin": "website",
                "root_site": root_url,
            }
            channels.append(ch)
            detail["channels"].append({"name": name, "url": m3u8})

        return

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
