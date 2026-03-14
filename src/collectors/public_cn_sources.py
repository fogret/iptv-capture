import os
import re
import json
import requests
from utils.logger import logger

def collect():
    logger.info("[public_cn] Collecting public CN sources...")

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
            text = fetch(url)
            if not text:
                continue

            if "#EXTM3U" in text or "#EXTINF" in text:
                channels += parse_m3u(text)
            elif text.strip().startswith("{") or text.strip().startswith("["):
                channels += parse_json(text)
            else:
                logger.warning(f"[public_cn] Unknown format: {url}")

    logger.info(f"[public_cn] Loaded {len(channels)} channels from public_cn")
    return channels


def fetch(url):
    try:
        return requests.get(url, timeout=8).text
    except:
        return ""


# -------------------------------
# M3U 解析
# -------------------------------
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
            group = extract(line, "group-title") or "未分组"

        elif line.startswith("http"):
            result.append({
                "name": name,
                "url": line,
                "logo": logo,
                "group": group
            })

    return result


# -------------------------------
# JSON 解析（支持 IPTV-API 格式）
# -------------------------------
def parse_json(text):
    result = []
    try:
        data = json.loads(text)
    except:
        return result

    if isinstance(data, list):
        for item in data:
            if "url" in item and "name" in item:
                result.append({
                    "name": item["name"],
                    "url": item["url"],
                    "logo": item.get("logo"),
                    "group": item.get("group", "未分组")
                })

    return result


def extract(line, key):
    if key + '="' in line:
        return line.split(key + '="')[1].split('"')[0]
    return None
