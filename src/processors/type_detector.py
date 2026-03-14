def detect_type(name):
    if any(k in name for k in ["体育", "sport", "球"]):
        return "体育"
    if any(k in name for k in ["电影", "movie", "影"]):
        return "电影"
    if any(k in name for k in ["新闻", "news"]):
        return "新闻"
    if any(k in name for k in ["综艺", "娱乐"]):
        return "综艺"
    if any(k in name for k in ["少儿", "儿童", "卡通"]):
        return "少儿"
    return "其他"


def run(channels):
    for ch in channels:
        ch["type"] = detect_type(ch["name"])
    return channels
