import os
import requests
from utils.logger import logger

def collect():
    logger.info("[public_cn] Loading source entry list from sources/public_cn.txt")

    path = "sources/public_cn.txt"
    if not os.path.exists(path):
        logger.warning("[public_cn] No public_cn.txt found, skip.")
        return []

    channels = []

    with open(path, "r", encoding="utf-8") as f:
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
    # 自动识别格式
    if "#EXTM3U" in text or "#EXTINF" in text:
        return parse_m3u(text)

    # 未来可以扩展 JSON / API
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
