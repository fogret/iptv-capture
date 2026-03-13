import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

def load_config():
    """
    加载项目根目录下的 config.json
    如果文件不存在，则返回一个默认配置，避免程序报错
    """
    if not os.path.exists(CONFIG_FILE):
        return {
            "quality_filter": {},
            "export": {
                "m3u_path": "output/channels.m3u",
                "tvbox_json_path": "output/tvbox.json"
            }
        }

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # 文件损坏时返回默认配置
        return {
            "quality_filter": {},
            "export": {
                "m3u_path": "output/channels.m3u",
                "tvbox_json_path": "output/tvbox.json"
            }
        }
