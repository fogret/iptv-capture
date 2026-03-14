import os
import requests
from utils.logger import logger

# 计算项目根目录（main.py 所在目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCES_DIR = os.path.join(BASE_DIR, "sources")
PUBLIC_CN_FILE = os.path.join(SOURCES_DIR, "public_cn.txt")

def collect():
    logger.info(f"[public_cn] Loading source entry list from {PUBLIC_CN_FILE}")

    if not os.path.exists(PUBLIC_CN_FILE):
        logger.warning("[public_cn] No public_cn.txt found, skip.")
        return []

    channels = []

    with open(PUBLIC_CN_FILE, "r", encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if not url:
                continue

            logger.info(f"[public_cn] Fetching: {url}")
            try:
                text = requests.get(url, timeout=10).text
                channels.extend(parse_source(text))
            except Exception as e:
                logger.error(f"[public_cn] Failed: {e}")

    logger.info(f"[public_cn] Loaded {len(channels)} channels from public_cn sources")
    return channels


def parse_source(text):
    if "#EXTM3U" in text or "#EXTINF" in text:
        return parse_m3u(text)
    return []


def parse_m3u(text):
    result = []
    lines = text.splitlines()

    name = None
    logo = None
    group = None

    for line in lines:
        line = line.strip()

        if line.startswith("#EXTINF"):
            name = extract(line, "tvg-name") or extract(line, "group-title") or "未知频道"
            logo = extract(line, "tvg-logo")

            if "CCTV" in name.upper():
                group = "央视"
            elif "卫视" in name:
                group = "卫视"
            else:
                group = "地方"

        elif line.startswith("http"):
            result.append({
                "name": name,
                "url": line,
                "logo": logo,
                "group": group
            })

    return result


def extract(line, key):
    if key + '="' in line:
        return line.split(key + '="')[1].split('"')[0]
    return None
