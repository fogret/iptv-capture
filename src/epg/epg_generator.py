import re
import os
from utils.logger import logger

def extract_channels(xml: str, tvg_ids: set):
    pattern = r'<channel id="([^"]+)">(.*?)</channel>'
    matches = re.findall(pattern, xml, flags=re.S)

    result = []
    for cid, block in matches:
        if cid in tvg_ids:
            result.append(f'<channel id="{cid}">{block}</channel>')
    return result

def extract_programmes(xml: str, tvg_ids: set):
    pattern = r'<programme start="[^"]+" stop="[^"]+" channel="([^"]+)">(.*?)</programme>'
    matches = re.findall(pattern, xml, flags=re.S)

    result = []
    for cid, block in matches:
        if cid in tvg_ids:
            result.append(f'<programme channel="{cid}">{block}</programme>')
    return result

def generate_epg(xml_data: str, channels, output_path="output/epg.xml"):
    tvg_ids = {ch["tvg_id"] for ch in channels if ch.get("tvg_id")}

    logger.info(f"[epg_generator] Filtering EPG for {len(tvg_ids)} channels")

    channel_blocks = extract_channels(xml_data, tvg_ids)
    programme_blocks = extract_programmes(xml_data, tvg_ids)

    final_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<tv>\n'
    final_xml += "\n".join(channel_blocks) + "\n"
    final_xml += "\n".join(programme_blocks) + "\n"
    final_xml += "</tv>"

    os.makedirs("output", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_xml)

    logger.info(f"[epg_generator] EPG generated: {output_path}")
