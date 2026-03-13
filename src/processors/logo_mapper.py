import os
import json
import requests
from utils.logger import logger

LOGO_DIR = "output/logos"

def load_logo_map():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "logo_map.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

LOGO_MAP = load_logo_map()

def download_logo(url: str, filename: str):
    os.makedirs(LOGO_DIR, exist_ok=True)
    path = os.path.join(LOGO_DIR, filename)

    if os.path.exists(path):
        return path

    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            with open(path, "wb") as f:
                f.write(resp.content)
            return path
    except:
        return None

def run(channels):
    logger.info("[logo_mapper] Start mapping logos...")

    for ch in channels:
        tvg_id = ch.get("tvg_id")
        name = ch["name"]

        logo_url = None

        # 1. 优先使用 tvg-id
        if tvg_id and tvg_id.lower() in LOGO_MAP:
            logo_url = LOGO_MAP[tvg_id.lower()]

        # 2. 再尝试频道名
        if not logo_url and name in LOGO_MAP:
            logo_url = LOGO_MAP[name]

        # 3. 如果仍然没有，跳过
        if not logo_url:
            ch["logo"] = None
            continue

        # 4. 下载 logo
        filename = f"{tvg_id or name}.png"
        local_path = download_logo(logo_url, filename)

        if local_path:
            # GitHub Raw URL（你需要替换 yourname/iptv-capture）
            ch["logo"] = f"https://raw.githubusercontent.com/yourname/iptv-capture/main/output/logos/{filename}"
        else:
            ch["logo"] = logo_url  # fallback

    logger.info("[logo_mapper] Done.")
    return channels
