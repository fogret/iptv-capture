import os

def add_headers(url):
    # 删除 UA 和 Referer，只返回原始 URL
    return url

def export_m3u(channels, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

        for ch in channels:
            if ch.get("disabled"):
                continue

            name = ch.get("name", "Unknown")
            group = ch.get("group", "未分组")
            url = add_headers(ch.get("url", ""))

            f.write(f'#EXTINF:-1 group-title="{group}",{name}\n')
            f.write(url + "\n")
