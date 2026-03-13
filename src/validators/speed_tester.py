import subprocess
import re
import time
from utils.logger import logger

FFPROBE_CMD = [
    "ffprobe",
    "-v", "error",
    "-select_streams", "v:0",
    "-show_entries", "stream=width,height,bit_rate",
    "-of", "default=noprint_wrappers=1:nokey=1"
]

def test_latency(url: str) -> float:
    start = time.time()
    try:
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-read_intervals", "%+1", "-i", url],
            stderr=subprocess.STDOUT,
            timeout=3
        )
        return round((time.time() - start) * 1000, 2)
    except:
        return None

def test_stream_info(url: str):
    try:
        cmd = FFPROBE_CMD + ["-i", url]
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=5).decode()

        lines = output.strip().split("\n")
        if len(lines) < 3:
            return None, None

        width = int(lines[0])
        height = int(lines[1])
        bitrate = int(lines[2]) if lines[2].isdigit() else None

        return (width, height), bitrate
    except:
        return None, None

def check(channels):
    logger.info("[speed_tester] Start speed testing...")

    for ch in channels:
        url = ch["url"]

        # 只测试 HTTP/HTTPS/UDP
        if not (url.startswith("http") or url.startswith("udp")):
            ch["latency"] = None
            ch["resolution"] = None
            ch["bitrate"] = None
            continue

        # 延迟
        latency = test_latency(url)
        ch["latency"] = latency

        # 分辨率 + 码率
        resolution, bitrate = test_stream_info(url)
        ch["resolution"] = resolution
        ch["bitrate"] = bitrate

    logger.info("[speed_tester] Done.")
    return channels
