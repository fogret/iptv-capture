import os

def collect():
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
    result = []

    if not os.path.exists(path):
        return result

    group_name = os.path.splitext(os.path.basename(path))[0]

    with open(path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            url = line.strip()
            if not url:
                continue

            name = f"{group_name}-{idx}"

            result.append({
                "name": name,
                "url": url,
                "组": group_name   # ★ 自动加上组
            })

    return result
