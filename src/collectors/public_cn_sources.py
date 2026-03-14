import os
import requests
from utils.logger import logger

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCES_DIR = os.path.join(BASE_DIR, "sources")
PUBLIC_CN_FILE = os.path.join(SOURCES_DIR, "public_cn.txt")

def collect():
    logger.info(f"[public_cn] 加载源列表: {PUBLIC_CN_FILE}")

    if not os.path.exists(PUBLIC_CN_FILE):
        logger.warning("[public_cn] public_cn.txt 不存在，跳过")
        return []

    channels = []

    with open(PUBLIC_CN_FILE, "r", encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if not url:
                continue

            logger.info(f"[public_cn] 获取: {url}")
            try:
                text = requests.get(url, timeout=10).text
                channels.extend(parse_source(text))
            except Exception as e:
                logger.error(f"[public_cn] 获取失败: {e}")

    logger.info(f"[public_cn] 共加载 {len(channels)} 条频道")
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
