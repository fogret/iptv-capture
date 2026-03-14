import os
import re
import json
import base64
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime

from utils.logger import logger
from utils.stats import stats
from utils.ua_manager import get_headers_for_url
from utils.channel_name import guess_channel_name      # ⭐ 新频道名识别
from utils.channel_group import guess_group            # ⭐ 新频道分组

# 路径保持不变
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCES_DIR = os.path.join(BASE_DIR, "sources")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

MAX_PAGES = 100
MAX_DEPTH = 3
MAX_CHANNELS = 200

AD_KEYWORDS = ["ad", "ads", "advert", "banner", "promo", "doubleclick", "googleads"]


def is_ad_url(url: str) -> bool:
    url_lower = url.lower()
    return any(k in url_lower for k in AD_KEYWORDS)


# ================================
# ⭐ 智能 UA + 自动识别真实 UA/Referer/Cookie/Host
# ================================
def fetch_html(url: str) -> str:
    try:
        headers = get_headers_for_url(url, mode="play")
        resp = requests.get(url, headers=headers, timeout=8)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
        html = resp.text

        # 自动识别真实参数
        real_ua = re.search(r'User-Agent["\']?\s*[:=]\s*["\']([^"\']+)', html)
        real_referer = re.search(r'Referer["\']?\s*[:=]\s*["\']([^"\']+)', html)
        real_cookie = re.search(r'Cookie["\']?\s*[:=]\s*["\']([^"\']+)', html)
        real_host = re.search(r'Host["\']?\s*[:=]\s*["\']([^"\']+)', html)

        if real_ua or real_referer or real_cookie or real_host:
            new_headers = {}
            if real_ua:
                new_headers["User-Agent"] = real_ua.group(1)
            if real_referer:
                new_headers["Referer"] = real_referer.group(1)
            if real_cookie:
                new_headers["Cookie"] = real_cookie.group(1)
            if real_host:
                host = real_host.group(1)
                new_headers["Host"] = host
                new_headers["Origin"] = f"https://{host}"

            try:
                resp2 = requests.get(url, headers=new_headers, timeout=8)
                resp2.raise_for_status()
                resp2.encoding = resp2.apparent_encoding
                return resp2.text
            except:
                pass

        return html

    except Exception as e:
        logger.warning(f"[websites] 抓取失败: {url} ({e})")
        return ""


# ================================
# ⭐ 全格式直播流提取器（增强版）
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
        r'https?://[^\s"\']+?\.mpd[^\s"\']*',
        r'https?://[^\s"\']+?\.f4m[^\s"\']*',
        r'rtmp://[^\s"\']+',
        r'https?://[^\s"\']+?live[^\s"\']*',
    ]

    for p in patterns:
        for m in re.findall(p, html, flags=re.IGNORECASE):
            urls.add(urljoin(base_url, m))

    # 3) JS 播放器配置
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

    # 4) iframe 深度解析
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src")
        if not src:
            continue
        iframe_url = urljoin(base_url, src)
        sub_html = fetch_html(iframe_url)
        if sub_html:
            sub_streams = extract_streams(sub_html, iframe_url)
            urls.update(sub_streams)

    # 5) HLS 深度解析
    m3u8_list = [u for u in urls if u.endswith(".m3u8")]

    for m3u8_url in m3u8_list:
        try:
            text = fetch_html(m3u8_url)
            if not text:
                continue

            for line in text.splitlines():
                line = line.strip()

                if line.endswith(".m3u8") and not line.startswith("#"):
                    urls.add(urljoin(m3u8_url, line))

                if line.endswith(".ts"):
                    urls.add(urljoin(m3u8_url, line))

                if line.startswith("#EXT-X-KEY"):
                    m = re.search(r'URI="([^"]+)"', line)
                    if m:
                        urls.add(urljoin(m3u8_url, m.group(1)))

        except:
            pass

    # 6) fetch / XHR 请求解析
    xhr_patterns = [
        r'fetch\(["\']([^"\']+)["\']',
        r'axios\.get\(["\']([^"\']+)["\']',
        r'\$\.get\(["\']([^"\']+)["\']',
        r'XMLHttpRequest\(["\']([^"\']+)["\']',
    ]

    for p in xhr_patterns:
        for api in re.findall(p, html, flags=re.IGNORECASE):
            api_url = urljoin(base_url, api)
            try:
                api_resp = requests.get(api_url, timeout=6)
                if api_resp.ok:
                    api_text = api_resp.text
                    for m in re.findall(r'https?://[^\s"\']+?\.m3u8[^\s"\']*', api_text):
                        urls.add(urljoin(api_url, m))
            except:
                pass

    # 7) base64 解码
    for b64 in re.findall(r'["\']([A-Za-z0-9+/=]{20,})["\']', html):
        try:
            decoded = base64.b64decode(b64).decode("utf-8", "ignore")
            if decoded.startswith("http"):
                urls.add(decoded)
        except:
            pass

    # 8) JSON 配置解析
    json_patterns = [
        r'playerConfig\s*=\s*({.*?})',
        r'video\s*=\s*({.*?})',
    ]

    for p in json_patterns:
        for block in re.findall(p, html, flags=re.DOTALL):
            try:
                data = json.loads(block)
                for key in ["url", "src", "file", "playurl"]:
                    if key in data and isinstance(data[key], str):
                        if data[key].startswith("http"):
                            urls.add(urljoin(base_url, data[key]))
            except:
                pass

    # 9) 直播平台适配（斗鱼 / 虎牙 / B站）
    if "douyu.com" in base_url:
        rid = re.findall(r'\d+', base_url)
        if rid:
            api = f"https://playweb.douyucdn.cn/lapi/live/getPlay/{rid[0]}"
            try:
                data = requests.get(api, timeout=6).json()
                real = data["data"]["rtmp_url"] + "/" + data["data"]["rtmp_live"]
                urls.add(real)
            except:
                pass

    if "huya.com" in base_url:
        for m in re.findall(r'"sStreamName":"([^"]+)"', html):
            real = f"https://al.hls.huya.com/src/{m}.m3u8"
            urls.add(real)

    if "bilibili.com" in base_url:
        for m in re.findall(r'"playurl":"([^"]+)"', html):
            urls.add(m.replace("\\/", "/"))

    # 10) 过滤点播 mp4
    urls = {u for u in urls if not u.lower().endswith(".mp4")}

    # 11) 过滤广告
    urls = {u for u in urls if not is_ad_url(u)}

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


# ================================
# ⭐ 递归抓取
# ================================
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

    streams = extract_streams(html, url)

    if streams:
        logger.info(f"[websites] 页面 {url} 发现 {len(streams)} 个直播流")

        for stream in streams:
            if is_ad_url(stream):
                logger.warning(f"[websites] 屏蔽广告源: {stream}")
                detail["ads_blocked"].append(stream)
                stats.website_ads_blocked_total += 1
                continue

            name = guess_channel_name(url, html)      # ⭐ 新频道名识别
            group = guess_group(name, url)            # ⭐ 新频道分组（基于名称+URL）

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

    links = extract_links(html, url)
    for link in links:
        logger.info(f"[websites] 递归进入子页面: {link}")
        collect_from_page(link, depth + 1, visited, channels, root_url)


# ================================
# ⭐ 网站抓取分析器（JSON + Markdown + 终端输出）
# ================================
def analyze_websites():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    analysis = {}

    for site, detail in stats.website_detail.items():
        entry = {
            "pages": detail["pages"],
            "max_depth": detail["max_depth"],
            "streams_found": len(detail["channels"]),
            "ads_blocked": len(detail["ads_blocked"]),
            "stream_types": [],
        }

        types = set()
        for ch in detail["channels"]:
            url = ch["url"].lower()
            if ".m3u8" in url:
                types.add("m3u8")
            elif ".flv" in url:
                types.add("flv")
            elif ".ts" in url:
                types.add("ts")
            elif "rtmp://" in url:
                types.add("rtmp")
        entry["stream_types"] = sorted(list(types))

        analysis[site] = entry

    # 保存 JSON
    json_path = os.path.join(OUTPUT_DIR, "website_analysis.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    # 保存 Markdown
    md_path = os.path.join(OUTPUT_DIR, "website_analysis.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# 网站抓取分析报告\n\n")
        f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for site, entry in analysis.items():
            f.write(f"## {site}\n")
            f.write(f"- 抓取页面数：{entry['pages']}\n")
            f.write(f"- 最大深度：{entry['max_depth']}\n")
            f.write(f"- 抓到直播流：{entry['streams_found']}\n")
            f.write(f"- 屏蔽广告：{entry['ads_blocked']}\n")
            f.write(f"- 流类型：{', '.join(entry['stream_types']) or '无'}\n\n")

    # 终端实时输出
    for site, entry in analysis.items():
        logger.info(
            f"\n[analysis] 网站: {site}\n"
            f"  - 抓取页面数: {entry['pages']}\n"
            f"  - 最大深度: {entry['max_depth']}\n"
            f"  - 抓到直播流: {entry['streams_found']}\n"
            f"  - 屏蔽广告: {entry['ads_blocked']}\n"
            f"  - 流类型: {', '.join(entry['stream_types']) or '无'}\n"
        )

    return analysis


# ================================
# ⭐ 主入口
# ================================
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

    analyze_websites()

    return channels
