import json
import os

# 正确读取仓库根目录的 config.json
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "config.json")
CONFIG_FILE = os.path.abspath(CONFIG_FILE)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {
            "quality_filter": {},
            "public_lists": [],
            "export": {
                "m3u_path": "output/channels.m3u",
                "tvbox_json_path": "output/tvbox.json"
            }
        }

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
