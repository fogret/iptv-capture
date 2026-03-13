from typing import List, Dict
from utils.logger import logger
from utils.config_loader import load_config

def collect() -> List[Dict]:
    cfg = load_config()
    result = []

    for item in cfg.get("custom_sources", []):
        logger.info(f"[custom_sources] Loaded custom: {item['name']}")
        result.append({
            "name": item["name"],
            "url": item["url"],
            "group": item.get("group", "Custom"),
            "tvg_id": item.get("tvg_id"),
            "source": "custom",
            "protocol": item["url"].split("://")[0],
        })

    return result
