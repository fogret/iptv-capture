import json
import os

LOGO_FILE = os.path.join(os.path.dirname(__file__), "logo_map.json")

def load_logo_map():
    try:
        with open(LOGO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # 文件损坏或不存在时，使用空映射 + fallback
        return {"_fallback": "https://live.fanmingming.com/tv/default.png"}

LOGO_MAP = load_logo_map()

def run(channels):
    for ch in channels:
        name = ch.get("name", "")
        ch["logo"] = LOGO_MAP.get(name, LOGO_MAP.get("_fallback"))
    return channels
