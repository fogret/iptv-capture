import re
import requests

QUALITY_MAP = {
    (3840, 2160): "4K",
    (2560, 1440): "2K",
    (1920, 1080): "1080p",
    (1280, 720): "720p",
    (854, 480): "480p",
    (640, 360): "360p",
    (426, 240): "240p",
}


def parse_resolution(line: str):
    m = re.search(r"RESOLUTION=(\d+)x(\d+)", line)
    if not m:
        return None
    w, h = int(m.group(1)), int(m.group(2))
    return w, h


def detect_quality_from_resolution(w: int, h: int) -> str:
    for (rw, rh), q in QUALITY_MAP.items():
        if w >= rw and h >= rh:
            return q
    return "未知"


def detect_quality_from_m3u8(url: str) -> dict:
    try:
        resp = requests.get(url, timeout=6)
        if not resp.ok:
            return {"quality": "未知", "bandwidth": None, "resolution": None}

        text = resp.text
        best_bandwidth = 0
        best_resolution = None

        for line in text.splitlines():
            line = line.strip()

            # 带宽
            if "BANDWIDTH=" in line:
                m = re.search(r"BANDWIDTH=(\d+)", line)
                if m:
                    bw = int(m.group(1))
                    if bw > best_bandwidth:
                        best_bandwidth = bw

            # 分辨率
            if "RESOLUTION=" in line:
                res = parse_resolution(line)
                if res:
                    best_resolution = res

        if best_resolution:
            w, h = best_resolution
            q = detect_quality_from_resolution(w, h)
            return {
                "quality": q,
                "bandwidth": best_bandwidth,
                "resolution": f"{w}x{h}",
            }

        return {
            "quality": "未知",
            "bandwidth": best_bandwidth or None,
            "resolution": None,
        }

    except:
        return {"quality": "未知", "bandwidth": None, "resolution": None}
