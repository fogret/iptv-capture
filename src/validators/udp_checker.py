import subprocess
from utils.logger import logger

def check(channels):
    result = []

    for ch in channels:
        url = ch["url"]
        if not (url.startswith("udp://") or "/udp/" in url):
            ch["udp_ok"] = None
            result.append(ch)
            continue

        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_name",
                "-of", "default=noprint_wrappers=1:nokey=1",
                url
            ]
            subprocess.check_output(cmd, timeout=5)
            ch["udp_ok"] = True
        except:
            ch["udp_ok"] = False

        result.append(ch)

    logger.info(f"[udp_checker] Checked {len(channels)} UDP channels")
    return result
