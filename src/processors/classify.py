def classify(name: str) -> str:
    if name.startswith("CCTV"):
        return "CCTV"
    if "卫视" in name:
        return "卫视"
    if "体育" in name:
        return "体育"
    if "电影" in name or "影视" in name:
        return "影视"
    return "其他"

def run(channels):
    for ch in channels:
        ch["group"] = classify(ch["name"])
    return channels
