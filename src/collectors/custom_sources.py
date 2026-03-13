import os

def load_custom_sources(path):
    channels = []

    # 如果 path 是目录 → 自动扫描所有 txt 文件
    if os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.endswith(".txt"):
                file_path = os.path.join(path, filename)
                channels.extend(parse_source_file(file_path))
    else:
        # 如果 path 是文件 → 兼容旧写法
        channels.extend(parse_source_file(path))

    return channels


def parse_source_file(file_path):
    channels = []
    if not os.path.exists(file_path):
        return channels

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "," not in line:
                continue

            name, url = line.split(",", 1)
            channels.append({
                "name": name.strip(),
                "url": url.strip()
            })

    return channels
