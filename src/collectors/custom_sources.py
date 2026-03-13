import os

def collect():
    """
    自动扫描 sources/ 目录下所有 .txt 文件
    并逐行解析成频道列表
    """
    base = "sources"
    channels = []

    if not os.path.exists(base):
        return channels

    for filename in os.listdir(base):
        if filename.endswith(".txt"):
            file_path = os.path.join(base, filename)
            channels.extend(parse_source_file(file_path))

    return channels


def parse_source_file(file_path):
    """
    解析单个 txt 文件
    格式：频道名,播放地址
    """
    result = []

    if not os.path.exists(file_path):
        return result

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "," not in line:
                continue

            name, url = line.split(",", 1)
            result.append({
                "name": name.strip(),
                "url": url.strip()
            })

    return result
