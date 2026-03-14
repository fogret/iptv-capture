import os
from utils.logger import logger

# 项目根目录（main.py 所在目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCES_DIR = os.path.join(BASE_DIR, "sources")

def collect():
    channels = []

    if not os.path.exists(SOURCES_DIR):
        logger.warning(f"[public_lists] 目录不存在: {SOURCES_DIR}")
        return channels

    for filename in os.listdir(SOURCES_DIR):
        if filename.endswith(".txt"):
            file_path = os.path.join(SOURCES_DIR, filename)
            channels.extend(parse_file(file_path))

    logger.info(f"[public_lists] 加载 {len(channels)} 条频道")
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
            result.append({
                "name": name.strip(),
                "url": url.strip()
            })

    return result
