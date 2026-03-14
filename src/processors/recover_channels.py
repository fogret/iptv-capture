import os
import json
from utils.logger import logger

def run(channels):
    """
    自动恢复系统：
    1. 检查被禁用频道是否恢复
    2. 评分达到恢复阈值 → 自动重新启用
    3. 输出恢复报告 recover.json
    """

    RECOVER_THRESHOLD = 70  # 恢复阈值（可写入 config.json）

    recovered = []
    report = []

    for ch in channels:
        name = ch.get("name", "")
        score = ch.get("score", 0)
        disabled = ch.get("disabled", False)

        # 记录监控信息
        report.append({
            "name": name,
            "score": score,
            "disabled": disabled
        })

        # 1. 如果频道被禁用，但评分恢复到阈值以上 → 自动恢复
        if disabled and score >= RECOVER_THRESHOLD:
            ch["disabled"] = False
            recovered.append(f"[RECOVER] {name} 已自动恢复（score={score}）")
            logger.info(f"[RECOVER] {name} 已自动恢复（score={score}）")

    # 2. 输出恢复报告
    os.makedirs("output", exist_ok=True)
    with open("output/recover.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 3. 输出恢复日志
    if recovered:
        logger.info("=== 频道恢复列表 ===")
        for r in recovered:
            logger.info(r)

    return channels
