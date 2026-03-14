import os
import json
from utils.logger import logger

def run(channels):
    """
    改进版自动禁用系统：
    - 不再因为一次失败就禁用
    - 连续 3 次失败才禁用
    - 评分、alive、speed_ok 都只会增加 fail_count，不会直接禁用
    - 央视/卫视保护，不会轻易禁用
    """

    FAIL_LIMIT = 3
    PROTECT_KEYWORDS = ["CCTV", "央视", "卫视"]

    report = []

    for ch in channels:
        name = ch.get("name", "")
        score = ch.get("score", 100)
        alive = ch.get("alive", True)
        speed_ok = ch.get("speed_ok", True)

        # 初始化 fail_count
        fail_count = ch.get("fail_count", 0)

        # 央视/卫视保护机制
        is_protected = any(k in name for k in PROTECT_KEYWORDS)

        # 评分低 → 增加失败次数
        if score < 40:
            fail_count += 1

        # alive=False → 增加失败次数
        if not alive:
            fail_count += 1

        # 测速失败 → 增加失败次数
        if not speed_ok:
            fail_count += 1

        # 更新 fail_count
        ch["fail_count"] = fail_count

        # 是否禁用
        disabled = False

        if not is_protected and fail_count >= FAIL_LIMIT:
            disabled = True
            logger.warning(f"[DISABLE] {name} 连续失败 {fail_count} 次 → 已禁用")

        ch["disabled"] = disabled

        report.append({
            "name": name,
            "score": score,
            "alive": alive,
            "speed_ok": speed_ok,
            "fail_count": fail_count,
            "protected": is_protected,
            "disabled": disabled
        })

    # 输出禁用报告
    os.makedirs("output", exist_ok=True)
    with open("output/disabled.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return channels
