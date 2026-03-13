import requests
from typing import List, Dict
from utils.logger import logger
from utils.config_loader import load_config

def parse_m3u(content: str) -> List[Dict]:
    lines = content.splitlines()
    channels = []
    name, tvg_id, group = None, None, None

    for line in lines:
        line = line.strip()
        if line.startswith("#EXTINF"):
            # 解析 EXTINF
            attrs = {}
            if "tvg-id" in line:
                try:
                    tvg_id = line.split('tvg-id="')[1].split('"')[0]
                except:
                    tvg_id = None
            if "group-title" in line:
                try:
                    group = line.split('group-title="')[1].split('"')[0]
                except:
                    group = None
            # 频道名
            name = line.split(",")[-1].strip()
        elif line and not line.startswith("#"):
            # URL 行
            url = line
            channels.append({
                "name": name,
                "url": url,
                "group": group,
                "tvg_id": tvg_id,
                "source": "public",
                "protocol": url.split("://")[0],
            })
            name, tvg_id, group = None, None, None

    return channels


def collect() -> List[Dict]:
    cfg = load_config()
    result = []

    for item in cfg.get("public_lists", []):
        url = item["url"]
        name = item["name"]
        logger.info(f"[public_lists] Fetching {name}: {url}")

        try:
            resp = requests.get(url, timeout=8)
            resp.raise_for_status()
            channels = parse_m3u(resp.text)
            logger.info(f"[public_lists] Parsed {len(channels)} channels from {name}")
            result.extend(channels)
        except Exception as e:
            logger.error(f"[public_lists] Failed to fetch {name}: {e}")

    return result
