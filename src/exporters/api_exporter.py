import json
import os
from utils.logger import logger

def export_channels(channels, path="output/api/channels.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)
    logger.info(f"[api_exporter] channels.json generated")


def export_groups(channels, path="output/api/groups.json"):
    groups = {}

    for ch in channels:
        group = ch["group"]
        if group not in groups:
            groups[group] = []
        groups[group].append(ch["name"])

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(groups, f, ensure_ascii=False, indent=2)
    logger.info(f"[api_exporter] groups.json generated")


def export_status(channels, path="output/api/status.json"):
    status = {}

    for ch in channels:
        status[ch["name"]] = {
            "ok": ch.get("ok"),
            "udp_ok": ch.get("udp_ok"),
            "latency": ch.get("latency"),
            "bitrate": ch.get("bitrate"),
            "resolution": ch.get("resolution")
        }

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)
    logger.info(f"[api_exporter] status.json generated")


def export_search_api(path="output/api/search.js"):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    js = """
async function searchChannels(q) {
  const res = await fetch('channels.json');
  const channels = await res.json();
  q = q.toLowerCase();
  return channels.filter(ch => ch.name.toLowerCase().includes(q));
}
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(js)

    logger.info(f"[api_exporter] search.js generated")
