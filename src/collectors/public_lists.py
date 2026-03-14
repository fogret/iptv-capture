import os
from utils.logger import logger

from .collect_websites import collect_websites

# 统一路径（与 universal_sources 完全一致）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCES_DIR = os.path.join(BASE_DIR, "sources")


def collect():
    channels = []

    if not os.path.exists(SOURCES_DIR):
        logger.warning(f"[public_lists] 目录不存在: {SOURCES_DIR}")
        return channels

    # ① 旧格式 TXT：name,url
    for filename in os.listdir(SOURCES_DIR):
        if filename.endswith(".txt"):
            file_path = os.path.join(SOURCES_DIR, filename)
            channels.extend(parse_file(file_path))

    # ② 网站抓取
    website_channels = collect_websites()
    channels.extend(website_channels)

    logger.info(
        f"[public_lists] 加载 {len(channels)} 条频道（含网站抓取 {len(website_channels)} 条）"
    )
    return channels


def parse_file(path):
    result = []

    if not os.path.exists(path):
        return result

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "," not in line:
                continue

            name, url = line.split(",", 1)
            result.append(
                {
                    "name": name.strip(),
                    "url": url.strip(),
                    "origin": "public_list",
                }
            )

    return result
