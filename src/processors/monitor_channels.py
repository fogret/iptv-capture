import os
import json
from utils.logger import logger

def run(channels):
    """
    自动监控系统：
    1. 记录每个频道的评分、延迟、可用性
    2. 评分下降自动报警
    3. 自动禁用低分频道
    4. 输出监控报告 monitor.json
    """

    report = []
    alerts = []

    # 阈值（可写入 config.json）
    DISABLE_THRESHOLD = 40
    ALERT_THRESHOLD = 60

    for ch in channels:
        name = ch.get("name", "")
        score = ch.get("score", 0)
        latency = ch.get("latency", 9999)
        alive = ch.get("alive", False)

        # 1. 记录监控信息
        report.append({
            "name": name,
            "url": ch.get("url", ""),
            "score": score,
            "latency": latency,
            "alive": alive,
            "group": ch.get("group", "未知")
        })

        # 2. 评分下降报警
        if score < ALERT_THRESHOLD:
            alerts.append(f"[ALERT] {name} 评分下降：score={score}")

        # 3. 自动禁用低分频道
        if score < DISABLE_THRESHOLD:
            ch["disabled"] = True
            logger.warning(f"[DISABLE] {name} 已自动禁用（score={score}）")
        else:
            ch["disabled"] = False

    # 4. 输出监控报告
    os.makedirs("output", exist_ok=True)
    with open("output/monitor.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 5. 输出报警日志
    if alerts:
        logger.warning("=== 频道报警列表 ===")
        for a in alerts:
            logger.warning(a)

    return channels
