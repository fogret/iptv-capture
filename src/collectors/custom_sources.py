import os

def collect():
    """
    自动扫描 sources/ 目录下所有 .txt 文件
    每行只写 URL，频道名自动生成
    """
    base = "sources"
    channels = []

    if not os.path.exists(base):
        return channels

    for filename in os.listdir(base):
        if filename.endswith(".txt"):
            file_path = os.path.join(base, filename)
            channels.extend(parse_file(file_path))

    return channels


def parse_file(path):
    """
    每行只写 URL，频道名自动生成：
    - 文件名作为分组
    - 行号作为频道序号
    """
    result = []

    if not os.path.exists(path):
        return result

    group_name = os.path.splitext(os.path.basename(path))[0]

    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            url = line.strip()
            if not url:
                continue

            # 自动生成频道名
            name = f"{group_name}-{idx}"

            result.append({
                "name": name,
                "url": url
            })

    return result
