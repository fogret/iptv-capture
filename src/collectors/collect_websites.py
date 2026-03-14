import os
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# 安全限制
MAX_PAGES = 100
MAX_DEPTH = 3
MAX_CHANNELS = 200

# 广告关键词
AD_KEYWORDS = ["ad", "ads", "advert", "banner", "promo", "doubleclick", "googleads"]


def is_ad_url(url: str) -> bool:
    """判断 URL 是否为广告"""
    url_lower = url.lower()
    return any(k in url_lower for k in AD_KEYWORDS)


def fetch_html(url: str) -> str:
    """抓取网页 HTML"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        resp = requests.get(url, headers=headers, timeout=8)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        return resp.text
    except:
        return ""


def extract_m3u8(html: str) -> list:
    """从 HTML 中提取所有 m3u8"""
    urls = set()

    # 1. video 标签
    soup = BeautifulSoup(html, "html.parser")
    for video in soup.find_all("video"):
        src = video.get("src")
        if src and src.endswith(".m3u8"):
            urls.add(src)

    # 2. hls.js 初始化
    matches = re.findall(r'["\'](https?://[^"\']+\.m3u8)["\']', html)
    for m in matches:
        urls.add(m)

    # 3. JS 变量
    matches = re.findall(r'(https?://[^"\']+\.m3u8)', html)
    for m in matches:
        urls.add(m)

    return list(urls)


def extract_links(html: str, base_url: str) -> list:
    """提取页面中的所有链接（用于递归）"""
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
    """自动识别频道名"""
    soup = BeautifulSoup(html, "html.parser")

    # 1. 网页标题
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
        if len(title) <= 20:
            return title

    # 2. 从 URL 推断
    m = re.search(r"(cctv\d+|hunantv|gzstv|channel\d+)", url.lower())
    if m:
        return m.group(1).upper()

    # 3. 默认
    return "未知频道"


def guess_group(url: str) -> str:
    """自动识别分组"""
    u = url.lower()
    if "cctv" in u:
        return "央视"
    if "tv" in u and "cctv" not in u:
        return "卫视"
    if "st" in u or "media" in u or "news" in u:
        return "地方台"
    return "其它"


def collect_from_page(url: str, depth: int, visited: set, channels: list):
    """递归抓取页面"""
    if depth > MAX_DEPTH or len(visited) > MAX_PAGES or len(channels) > MAX_CHANNELS:
        return

    if url in visited:
        return
    visited.add(url)

    html = fetch_html(url)
    if not html:
        return

    # 解析 m3u8
    m3u8_list = extract_m3u8(html)

    # 单页模式 / 多频道模式
    if m3u8_list:
        for m3u8 in m3u8_list:
            if is_ad_url(m3u8):
                continue

            name = guess_channel_name(url, html)
            group = guess_group(url)

            channels.append({
                "name": name,
                "group": group,
                "url": m3u8,
                "origin": "website"
            })
        return

    # 递归模式：没有 m3u8 → 继续找子页面
    links = extract_links(html, url)
    for link in links:
        collect_from_page(link, depth + 1, visited, channels)


def collect_websites():
    """主入口：扫描 sources/ 下所有 txt 并抓取网站"""
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sources")
    channels = []

    for file in os.listdir(base_dir):
        if not file.endswith(".txt"):
            continue

        path = os.path.join(base_dir, file)
        if os.path.getsize(path) == 0:
            continue

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                url = line.strip()
                if not url or url.startswith("#"):
                    continue
                if not url.startswith("http"):
                    continue

                visited = set()
                collect_from_page(url, 1, visited, channels)

    return channels
