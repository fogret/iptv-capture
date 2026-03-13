from utils.logger import logger

DEFAULT_MIN_WIDTH = 1280
DEFAULT_MIN_HEIGHT = 720
DEFAULT_MIN_BITRATE = 1500000   # 1.5 Mbps
DEFAULT_MAX_LATENCY = 1500      # ms

def run(channels, cfg=None):
    if cfg:
        min_width = cfg.get("min_width", DEFAULT_MIN_WIDTH)
        min_height = cfg.get("min_height", DEFAULT_MIN_HEIGHT)
        min_bitrate = cfg.get("min_bitrate", DEFAULT_MIN_BITRATE)
        max_latency = cfg.get("max_latency", DEFAULT_MAX_LATENCY)
    else:
        min_width = DEFAULT_MIN_WIDTH
        min_height = DEFAULT_MIN_HEIGHT
        min_bitrate = DEFAULT_MIN_BITRATE
        max_latency = DEFAULT_MAX_LATENCY

    filtered = []

    for ch in channels:
        # 1. 必须可用
        if ch.get("ok") is False and ch.get("udp_ok") is False:
            continue

        # 2. 延迟过滤
        latency = ch.get("latency")
        if latency is not None and latency > max_latency:
            continue

        # 3. 分辨率过滤
        resolution = ch.get("resolution")
        if resolution:
            w, h = resolution
            if w < min_width or h < min_height:
                continue

        # 4. 码率过滤
        bitrate = ch.get("bitrate")
        if bitrate is not None and bitrate < min_bitrate:
            continue

        filtered.append(ch)

    logger.info(f"[filter_quality] {len(channels)} → {len(filtered)} after quality filter")
    return filtered
