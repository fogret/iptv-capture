import os
import requests
from utils.logger import logger

# 项目根目录（main.py 所在目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOURCES_DIR = os.path.join(BASE_DIR, "sources")


def collect():
    channels = []

    if not os.path.exists(SOURCES_DIR):
        logger.warning(f"[sources] 目录不存在: {SOURCES_DIR}")
        return channels

    logger.info(f"[sources] 扫描目录: {SOURCES_DIR}")

    for filename in os.listdir(SOURCES_DIR):
        if filename.endswith(".txt"):
            file_path = os.path.join(SOURCES_DIR, filename)
            logger.info(f"[sources] 读取文件: {file_path}")
            channels.extend(parse_file(file_path))

    logger.info(f"[sources] 共加载 {len(channels)} 条频道")
    return channels


# ============================
# 解析单个 TXT 文件
# ============================
def parse_file(path):
    result = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            # 1. name,url 格式
            if "," in line:
                name, url = line.split(",", 1)
                result.append(build_channel(name.strip(), url.strip()))
                continue

            # 2. URL-only（HTTP/HLS/M3U）
            if line.startswith("http"):
                # 如果是 M3U 链接，下载解析
                if line.endswith(".m3u") or line.endswith(".m3u8"):
                    try:
                        text = requests.get(line, timeout=10).text
                        result.extend(parse_m3u(text))
                    except Exception as e:
                        logger.error(f"[sources] M3U 获取失败: {e}")
                else:
                    result.append(build_channel("未知频道", line))
                continue

            # 3. UDP 组播
            if line.startswith("udp://") or line.startswith("rtp://"):
                result.append({
                    "name": "组播频道",
                    "url": line,
                    "group": "组播"
                })
                continue

    return result


# ============================
# M3U 解析
# ============================
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

            # 自动分组
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


# ============================
# 工具函数
# ============================
def extract(line, key):
    if key + '="' in line:
        return line.split(key + '="')[1].split('"')[0]
    return None


def build_channel(name, url):
    # 自动分组
    if "CCTV" in name.upper():
        group = "央视"
    elif "卫视" in name:
        group = "卫视"
    else:
        group = "地方"

    return {
        "name": name,
        "url": url,
        "group": group
            }
