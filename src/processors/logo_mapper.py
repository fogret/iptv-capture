import json
import os

def run(channels):
    logo_map = load_logo_map()

    for ch in channels:
        name = ch.get("name", "")
        if name in logo_map:
            ch["logo"] = logo_map[name]
        else:
            # fallback：央视/卫视自动匹配
            if name.startswith("CCTV-"):
                ch["logo"] = f"https://live.fanmingming.com/tv/{name}.png"
            elif "卫视" in name:
                ch["logo"] = f"https://live.fanmingming.com/tv/{name}.png"

    return channels


def load_logo_map():
    path = "sources/logos.json"
    if not os.path.exists(path):
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}
