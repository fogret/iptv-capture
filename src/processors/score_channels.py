import re

def run(channels):
    for ch in channels:
        score = 0

        # -------------------------------
        # 1. 可用性（availability）
        # -------------------------------
        # http_checker / udp_checker 会写入 ch["alive"] = True/False
        alive = ch.get("alive", False)
        score += 40 if alive else 0

        # -------------------------------
        # 2. 稳定性（stability）
        # -------------------------------
        # speed_tester 会写入 ch["speed_ok"] = True/False
        stable = ch.get("speed_ok", False)
        score += 30 if stable else 0

        # -------------------------------
        # 3. 清晰度（quality）
        # -------------------------------
        url = ch.get("url", "")
        if "1080" in url:
            score += 20
        elif "720" in url:
            score += 15
        elif "480" in url:
            score += 10
        else:
            score += 5

        # -------------------------------
        # 4. 延迟（latency）
        # -------------------------------
        # speed_tester 会写入 ch["latency"]（毫秒）
        latency = ch.get("latency", 9999)

        if latency < 200:
            score += 10
        elif latency < 500:
            score += 7
        elif latency < 1000:
            score += 4
        else:
            score += 1

        ch["score"] = score

    return channels
