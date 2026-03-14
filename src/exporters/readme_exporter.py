# exporters/readme_exporter.py
# 极简版 README：更新时间 + 总数 + 新增数量 + 减少数量

import json
from datetime import datetime

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def export_readme(channels, stats, path="README.md"):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

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

自动更新 · GitHub Actions 驱动
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
