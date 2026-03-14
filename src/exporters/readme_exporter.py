# exporters/readme_exporter.py
# 最终完整版：新增频道 + 徽章 + 运行状态 + 彩色图表 + 统计信息（无订阅地址，无来源统计）

import json
import os
from datetime import datetime
from collections import Counter

# ANSI 颜色
COLOR_MAP = {
    "央视": "\033[91m",
    "卫视": "\033[93m",
    "地方台": "\033[94m",
    "其它": "\033[92m",
    "未知": "\033[90m",
}
RESET = "\033[0m"


def ascii_bar(value, max_value, width=30):
    if max_value == 0:
        return ""
    bar_len = int(value / max_value * width)
    return "█" * bar_len


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def export_readme(channels, stats, path="README.md"):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    total = len(channels)

    # -------------------------
    # 1. 今日新增频道
    # -------------------------
    PREV_PATH = "output/channels_prev.json"
    prev_channels = load_json(PREV_PATH)

    prev_set = {(c.get("name"), c.get("url")) for c in prev_channels}
    curr_set = {(c.get("name"), c.get("url")) for c in channels}

    added = curr_set - prev_set
    added_list = [f"- {name}  ({url})" for name, url in added]
