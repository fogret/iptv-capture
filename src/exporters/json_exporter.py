import os
import json

def add_headers(url):
    # 删除 UA 和 Referer，只返回原始 URL
    return url

def export_tvbox(channels, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    data = []
    for ch in channels:
        if ch.get("disabled"):
            continue

        data.append({
            "name": ch.get("name", ""),
            "url": add_headers(ch.get("url", "")),
            "group": ch.get("group", "未分组")
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
