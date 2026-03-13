
import requests
from typing import List, Dict
from utils.logger import logger

def check(channels: List[Dict]) -> List[Dict]:
    result = []

    for ch in channels:
        url = ch["url"]
        if not url.startswith("http"):
            ch["ok"] = None
            result.append(ch)
            continue

        try:
            resp = requests.get(url, timeout=3, stream=True)
            ch["ok"] = resp.status_code == 200
        except:
            ch["ok"] = False

        result.append(ch)

    logger.info(f"[http_checker] Checked {len(channels)} channels")
    return result
