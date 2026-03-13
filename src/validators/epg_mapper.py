import json
import os

def load_mapping():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "tvg_map.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

TVG_MAP = load_mapping()

def guess_tvg_id(name: str):
    if name in TVG_MAP:
        return TVG_MAP[name]
    if name.startswith("CCTV"):
        num = name.replace("CCTV", "").replace("-", "").strip()
        if num.isdigit():
            return f"cctv{num}"
    return None

def run(channels):
    for ch in channels:
        if not ch.get("tvg_id"):
            ch["tvg_id"] = guess_tvg_id(ch["name"])
    return channels
