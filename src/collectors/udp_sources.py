import os
from utils.logger import logger

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCES_DIR = os.path.join(BASE_DIR, "sources")
UDP_FILE = os.path.join(SOURCES_DIR, "udp.txt")

def collect():
    channels = []

    if not os.path.exists(UDP_FILE):
        logger.warning(f"[udp_sources] 文件不存在: {UDP_FILE}")
        return channels

    with open(UDP_FILE, "r", encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if not url:
                continue

            channels.append({
                "name": "组播频道",
                "url": url,
                "group": "组播"
            })

    logger.info(f"[udp_sources] 加载 {len(channels)} 条组播频道")
    return channels
