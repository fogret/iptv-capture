import os
from utils.logger import logger

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCES_DIR = os.path.join(BASE_DIR, "sources")
CUSTOM_FILE = os.path.join(SOURCES_DIR, "custom.txt")

def collect():
    channels = []

    if not os.path.exists(CUSTOM_FILE):
        logger.warning(f"[custom_sources] 文件不存在: {CUSTOM_FILE}")
        return channels

    with open(CUSTOM_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "," not in line:
                continue

            name, url = line.split(",", 1)
            channels.append({
                "name": name.strip(),
                "url": url.strip()
            })

    logger.info(f"[custom_sources] 加载 {len(channels)} 条频道")
    return channels
