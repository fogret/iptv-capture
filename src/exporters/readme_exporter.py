---

```python
# exporters/readme_exporter.py
# 最终完整版：新增频道 + 徽章 + 运行状态 + 彩色图表 + 统计信息（无订阅地址）

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
    added_block = "\n".join(added_list) if added_list else "（今日无新增频道）"

    # -------------------------
    # 2. 分类统计
    # -------------------------
    groups = Counter([c.get("group", "未知") for c in channels])
    groups_sorted = sorted(groups.items(), key=lambda x: x[1], reverse=True)
    max_group_value = groups_sorted[0][1] if groups_sorted else 0

    color_chart = "\n".join(
        f"{COLOR_MAP.get(name, '\033[95m')}{name:<6} {ascii_bar(count, max_group_value)} {count}{RESET}"
        for name, count in groups_sorted
    )

    # -------------------------
    # 3. 来源统计
    # -------------------------
    origins = Counter([c.get("origin", "unknown") for c in channels])

    # -------------------------
    # 4. UA 统计
    # -------------------------
    ua_need = sum(1 for c in channels if c.get("need_ua"))
    ua_no = total - ua_need

    # -------------------------
    # 5. HLS 深度解析统计
    # -------------------------
    hls_key = stats.get("hls_key_total", 0)
    hls_ts = stats.get("hls_ts_total", 0)
    hls_sub = stats.get("hls_sub_m3u8_total", 0)

    # -------------------------
    # 6. 网站抓取统计
    # -------------------------
    website_pages = stats.get("website_pages_total", 0)
    website_ads = stats.get("website_ads_blocked_total", 0)

    # -------------------------
    # 7. README 内容（无订阅地址）
    # -------------------------
    content = f"""# IPTV Live

![Build Status](https://github.com/fogret/IPTV-Capture/actions/workflows/main.yml/badge.svg)
![Stars](https://img.shields.io/github/stars/fogret/IPTV-Capture?style=flat-square)
![Forks](https://img.shields.io/github/forks/fogret/IPTV-Capture?style=flat-square)
![License](https://img.shields.io/github/license/fogret/IPTV-Capture?style=flat-square)

自动更新的 IPTV 直播源列表  
更新时间：**{now}**  
频道总数：**{total}**

---

## 🆕 今日新增频道
{added_block}

---

## 📊 频道分类统计（彩色图表 + 自动排序）

```ansi
{color_chart}
