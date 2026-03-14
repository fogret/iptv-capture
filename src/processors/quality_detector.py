def detect_quality(name, url):
    text = (name + url).lower()

    if "4k" in text or "2160" in text:
        return "4K"
    if "1080" in text or "fullhd" in text:
        return "1080P"
    if "720" in text or "hd" in text:
        return "720P"
    return "SD"


def run(channels):
    for ch in channels:
        ch["quality"] = detect_quality(ch["name"], ch["url"])
    return channels
