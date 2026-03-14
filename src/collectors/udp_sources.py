import os
import re
from utils.logger import logger

def collect():
    """
    从 sources/udp*.txt 读取组播源入口
    自动识别 udpxy / udp://
    自动生成频道对象
    """
    logger.info("[udp] Collecting UDP / multicast sources...")

    base = "sources"
    channels = []

    if not os.path.exists(base):
        return channels

    # 处理所有 udp*.txt 文件
    for filename in os.listdir(base):
        if filename.startswith("udp") and filename.endswith(".txt"):
            path = os.path.join(base, filename)
            channels += parse_udp_file(path)

    logger.info(f"[udp] Loaded {len(channels)} UDP channels")
    return channels


def parse_udp_file(path):
    result = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if not url:
                continue

            # udpxy 格式：http://router:4022/udp/239.1.1.1:8000
            if url.startswith("http://") and "/udp/" in url:
                name = extract_multicast_name(url)
                result.append({
                    "name": name,
                    "url": url,
                    "group": "组播"
                })
                continue

            # 原生 udp://@239.1.1.1:8000
            if url.startswith("udp://"):
                name = extract_multicast_name(url)
                result.append({
                    "name": name,
                    "url": url,
                    "group": "组播"
                })
                continue

    return result


def extract_multicast_name(url):
    """
    从 URL 中提取组播地址作为频道名
    """
    match = re.search(r"(\d+\.\d+\.\d+\.\d+):(\d+)", url)
    if match:
        ip = match.group(1)
        port = match.group(2)
        return f"组播 {ip}:{port}"

    return "组播频道"
