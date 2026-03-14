import os
from collections import defaultdict

DEFAULT_UA = (
    "User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)
DEFAULT_REFERER = "Referer=https://www.google.com/"

def add_headers(url):
    if not url.startswith("http"):
        return url
    return f"{url}|{DEFAULT_UA}&{DEFAULT_REFERER}"

def export_txt(channels, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 按 group 分组
    groups = defaultdict(list)
    for ch in channels:
        if ch.get("disabled"):
            continue
        group = ch.get("group", "未分组")
        groups[group].append(ch)

    with open(output_path, "w", encoding="utf-8") as f:
        for group_name, ch_list in groups.items():
            f.write(f"========== {group_name} ==========\n")

            # 每个分组内自动编号
            for idx, ch in enumerate(ch_list, start=1):
                name = ch.get("name", "Unknown")
                url = add_headers(ch.get("url", ""))

                f.write(f"{idx}. {name},{url}\n")

            f.write("\n")  # 分组之间空一行
