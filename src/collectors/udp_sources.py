import os
from utils.logger import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCES_DIR = os.path.join(BASE_DIR, "sources")

def collect():
    channels = []

    if not os.path.exists(SOURCES_DIR):
        logger.warning(f"[udp_sources] 目录不存在: {SOURCES_DIR}")
        return channels

    for filename in os.listdir(SOURCES_DIR):
        if filename.endswith(".txt"):
            file_path = os.path.join(SOURCES_DIR, filename)
            channels.extend(parse_file(file_path))

    logger.info(f"[udp_sources] 加载 {len(channels)} 条组播频道")
    return channels


def parse_file(path):
    result = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if not url:
                continue

            result.append({
                "name": "组播频道",
                "url": url,
                "group": "组播"
            })

    return result
