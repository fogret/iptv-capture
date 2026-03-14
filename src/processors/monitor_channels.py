import os
import json
from utils.logger import logger

def run(channels):
    """
    改进版自动监控系统：
    - 不再直接禁用频道
    - 评分下降 → 增加 fail_count
    - alive=False → 增加 fail_count
    - speed_ok=False → 增加 fail_count
    - fail_count 达到阈值后由 disable_channels 处理
    - 输出监控报告 monitor.json
    """

    ALERT_THRESHOLD = 60
    FAIL_SCORE_THRESHOLD = 40
    FAIL_LATENCY_THRESHOLD = 3000  # ms
    FAIL_LIMIT = 3

    report = []
    alerts = []

    for ch in channels:
        name = ch.get("name", "")
        score = ch.get("score", 100)
        latency = ch.get("latency", 9999)
        alive = ch.get("alive", True)
        speed_ok = ch.get("speed_ok", True)

        # 初始化 fail_count
        fail_count = ch.get("fail_count", 0)

        # 记录监控信息
        report.append({
            "name": name,
            "url": ch.get("url", ""),
            "score": score,
            "latency": latency,
            "alive": alive,
            "speed_ok": speed_ok,
            "fail_count": fail_count,
            "group": ch.get("group", "未知")
        })

        # 评分下降报警
        if score < ALERT_THRESHOLD:
            alerts.append(f"[ALERT] {name} 评分下降：score={score}")

        # 以下逻辑只增加 fail_count，不直接禁用
        if score < FAIL_SCORE_THRESHOLD:
            fail_count += 1

        if not alive:
            fail_count += 1

        if not speed_ok:
            fail_count += 1

        if latency > FAIL_LATENCY_THRESHOLD:
            fail_count += 1

        # 更新 fail_count
        ch["fail_count"] = fail_count

        # 禁用逻辑交给 disable_channels 处理
        if fail_count >= FAIL_LIMIT:
            logger.warning(f"[MONITOR] {name} 连续失败 {fail_count} 次 → 将在禁用阶段处理")

    # 输出监控报告
    os.makedirs("output", exist_ok=True)
    with open("output/monitor.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 输出报警日志
    if alerts:
        logger.warning("=== 频道报警列表 ===")
        for a in alerts:
            logger.warning(a)

    return channels
