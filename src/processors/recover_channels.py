import os
import json
from utils.logger import logger

def run(channels):
    """
    改进版自动恢复系统：
    - 不再只看评分
    - 评分恢复 + alive=True + speed_ok=True → 自动恢复
    - fail_count 自动清零
    - 央视/卫视优先恢复
    """

    RECOVER_SCORE = 60
    PROTECT_KEYWORDS = ["CCTV", "央视", "卫视"]

    recovered = []
    report = []

    for ch in channels:
        name = ch.get("name", "")
        score = ch.get("score", 0)
        disabled = ch.get("disabled", False)
        alive = ch.get("alive", True)
        speed_ok = ch.get("speed_ok", True)
        fail_count = ch.get("fail_count", 0)

        is_protected = any(k in name for k in PROTECT_KEYWORDS)

        report.append({
            "name": name,
            "score": score,
            "alive": alive,
            "speed_ok": speed_ok,
            "fail_count": fail_count,
            "disabled": disabled,
            "protected": is_protected
        })

        # 条件：被禁用 + 状态恢复正常
        if disabled:
            # 央视/卫视优先恢复
            if is_protected and alive:
                ch["disabled"] = False
                ch["fail_count"] = 0
                recovered.append(f"[RECOVER] {name}（央视/卫视优先恢复）")
                logger.info(f"[RECOVER] {name}（央视/卫视优先恢复）")
                continue

            # 普通频道恢复条件
            if score >= RECOVER_SCORE and alive and speed_ok:
                ch["disabled"] = False
                ch["fail_count"] = 0
                recovered.append(f"[RECOVER] {name}（score={score}）")
                logger.info(f"[RECOVER] {name}（score={score}）")

    # 输出恢复报告
    os.makedirs("output", exist_ok=True)
    with open("output/recover.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    if recovered:
        logger.info("=== 自动恢复频道列表 ===")
        for r in recovered:
            logger.info(r)

    return channels
