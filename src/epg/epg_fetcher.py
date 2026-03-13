import requests
import yaml
import os
from utils.logger import logger

def load_sources():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "epg_sources.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["sources"]

def fetch_epg():
    sources = load_sources()
    xml_data = ""

    for src in sources:
        logger.info(f"[epg_fetcher] Fetching EPG from {src['name']} ({src['url']})")
        try:
            resp = requests.get(src["url"], timeout=10)
            if resp.status_code == 200:
                xml_data += resp.text
        except Exception as e:
            logger.error(f"[epg_fetcher] Failed: {e}")

    return xml_data
