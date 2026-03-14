import os
import json
from utils.logger import logger

def run(channels):
    """
    自动禁用系统：
    1. 根据评分自动禁用
    2. 根据可用性自动禁用
    3. 根据测速结果自动禁用
    4. 输出禁用报告 disabled.json
    """

    DISABLE_SCORE_THRESHOLD = 40     # 评分低于 40 自动禁用
    DISABLE_ALIVE_REQUIRED = True    # alive=False 自动禁用
    DISABLE_SPEED_REQUIRED = True    # speed_ok=False 自动禁用

    disabled_list = []
    report = []

    for ch in channels:
        name = ch.get("name", "")
        score = ch.get("score", 0)
        alive = ch.get("alive", False)
        speed_ok = ch.get("speed_ok", False)

        disabled = False

        # 1. 评分过低 → 禁用
        if score < DISABLE_SCORE_THRESHOLD:
            disabled = True
            logger.warning(f"[DISABLE] {name} 因评分过低被禁用（score={score}）")

        # 2. 不可用 → 禁用
        if DISABLE_ALIVE_REQUIRED and not alive:
            disabled = True
            logger.warning(f"[DISABLE] {name} 因不可用被禁用（alive=False）")

        # 3. 测速失败 → 禁用
        if DISABLE_SPEED_REQUIRED and not speed_ok:
            disabled = True
            logger.warning(f"[DISABLE] {name} 因测速失败被禁用（speed_ok=False）")

        ch["disabled"] = disabled

        if disabled:
            disabled_list.append(name)

        report.append({
            "name": name,
            "score": score,
            "alive": alive,
            "speed_ok": speed_ok,
            "disabled": disabled
        })

    # 输出禁用报告
    os.makedirs("output", exist_ok=True)
    with open("output/disabled.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    if disabled_list:
        logger.warning("=== 自动禁用频道列表 ===")
        for name in disabled_list:
            logger.warning(f"- {name}")

    return channels
