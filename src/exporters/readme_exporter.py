# exporters/readme_exporter.py
# 极简版 README：北京时间 + 总数 + 新增数量 + 减少数量 + 法律说明

import json
from datetime import datetime, timedelta

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def export_readme(channels, stats, path="README.md"):
    # 北京时间（UTC+8）
    now = (datetime.utcnow() + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M CST")

    # 当前频道
    curr_set = {(c.get("name"), c.get("url")) for c in channels}

    # 之前的频道
    prev_channels = load_json("output/channels_prev.json")
    prev_set = {(c.get("name"), c.get("url")) for c in prev_channels}

    # 新增 & 减少数量
    added_count = len(curr_set - prev_set)
    removed_count = len(prev_set - curr_set)

    # 写入 README
    content = f"""# IPTV 自动聚合

**更新时间：** {now}  
**当前频道总数：** {len(channels)}  

---

## 今日变化
- **新增频道数：** {added_count}  
- **减少频道数：** {removed_count}  

---

## 法律声明
本项目仅对公开可访问的直播源进行技术性聚合，不提供、存储或传播任何受版权保护的付费内容。  
所有内容仅供个人学习、技术研究与网络协议分析使用，**不构成任何形式的转播、传播或商业用途**。  
如某些源涉及版权，请在 24 小时内自行删除；版权方如有异议，可随时联系移除相关链接。

---

自动更新 · GitHub Actions 驱动
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
