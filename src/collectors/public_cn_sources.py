import os
import requests
from utils.logger import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCES_DIR = os.path.join(BASE_DIR, "sources")

def collect():
    channels = []

    if not os.path.exists(SOURCES_DIR):
        logger.warning(f"[public_cn] 目录不存在: {SOURCES_DIR}")
        return channels

    for filename in os.listdir(SOURCES_DIR):
        if filename.endswith(".txt"):
            file_path = os.path.join(SOURCES_DIR, filename)
            channels.extend(load_from_file(file_path))

    logger.info(f"[public_cn] 共加载 {len(channels)} 条频道")
    return channels


def load_from_file(path):
    result = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if not url:
                continue

            try:
                text = requests.get(url, timeout=10).text
                result.extend(parse_source(text))
            except Exception as e:
                logger.error(f"[public_cn] 获取失败: {e}")

    return result


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
