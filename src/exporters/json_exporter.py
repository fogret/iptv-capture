import os
import json

DEFAULT_UA = (
    "User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
DEFAULT_REFERER = "Referer=https://www.google.com/"

def add_headers(url):
    if not url.startswith("http"):
        return url
    return f"{url}|{DEFAULT_UA}&{DEFAULT_REFERER}"

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
