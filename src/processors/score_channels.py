import re

def run(channels):
    for ch in channels:
        score = 0

        # -------------------------------
        # 1. 可用性（alive）
        # -------------------------------
        alive = ch.get("alive", False)
        score += 30 if alive else 0

        # -------------------------------
        # 2. 稳定性（speed_ok）
        # -------------------------------
        stable = ch.get("speed_ok", False)
        score += 25 if stable else 0

        # -------------------------------
        # 3. 清晰度（quality）
        # -------------------------------
        url = ch.get("url", "")
        quality = ch.get("quality", "")

        if "1080" in url or "FHD" in quality:
            score += 20
        elif "720" in url or "HD" in quality:
            score += 15
        elif "480" in url or "SD" in quality:
            score += 10
        else:
            score += 5

        # -------------------------------
        # 4. 延迟（latency）
        # speed_tester 测的是下载速度，不是毫秒延迟
        # 所以我们用 speed 值来估算
        # -------------------------------
        speed = ch.get("speed", 0)

        if speed > 50000:        # >50KB
            score += 15
        elif speed > 20000:      # >20KB
            score += 10
        elif speed > 5000:       # >5KB
            score += 5
        else:
            score += 1

        # -------------------------------
        # 5. 频道类型加权（央视/卫视）
        # -------------------------------
        name = ch.get("name", "")
        if any(k in name for k in ["CCTV", "央视"]):
            score += 10
        elif "卫视" in name:
            score += 5

        # -------------------------------
        # 6. fallback 修复加分
        # -------------------------------
        if ch.get("fixed", False):
            score += 5

        # -------------------------------
        # 7. 限制最大分数
        # -------------------------------
        score = min(score, 100)

        ch["score"] = score

    return channels
