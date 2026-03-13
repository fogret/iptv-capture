import json
from utils.config_loader import load_config

def export_tvbox(channels, path):
    cfg = load_config()

    data = {
        "name": cfg["export"].get("tvbox_name", "IPTV直播"),
        "type": 0,
        "url": cfg["export"]["m3u_path"],
        "epg": "https://raw.githubusercontent.com/yourname/iptv-capture/main/output/epg.xml",
        "logo": cfg["export"].get("tvbox_logo", "")
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
