from utils.logger import logger

PROTOCOL_PRIORITY = ["http", "https", "rtmp", "udp"]
SOURCE_PRIORITY = ["custom", "public"]

def run(channels):
    merged = {}

    for ch in channels:
        key = ch["name"]

        if key not in merged:
            merged[key] = ch
            continue

        old = merged[key]

        # 协议优先级
        if PROTOCOL_PRIORITY.index(ch["protocol"]) < PROTOCOL_PRIORITY.index(old["protocol"]):
            merged[key] = ch
            continue

        # 来源优先级
        if SOURCE_PRIORITY.index(ch["source"]) < SOURCE_PRIORITY.index(old["source"]):
            merged[key] = ch
            continue

    logger.info(f"[deduplicate] {len(channels)} → {len(merged)} after dedup")
    return list(merged.values())
