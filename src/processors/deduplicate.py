import re
from difflib import SequenceMatcher

# -----------------------------------
# URL 归一化（去掉 token、ts、udpxy 等）
# -----------------------------------
def normalize_url(url: str) -> str:
    if not url:
        return ""

    # 去掉 udpxy 前缀
    url = url.replace("/udp/", "").replace("udp://@", "udp://")

    # 去掉 token、ts、sign 等参数
    url = re.sub(r"[?&](token|ts|sign|auth|expires)=[^&]+", "", url, flags=re.IGNORECASE)

    return url


# -----------------------------------
# 名称相似度
# -----------------------------------
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


# -----------------------------------
# 判断两个频道是否为同一频道
# -----------------------------------
def is_same_channel(a, b):
    name_a = a["name"]
    name_b = b["name"]

    # 完全相同
    if name_a == name_b:
        return True

    # CCTV 特殊处理
    if name_a.startswith("CCTV-") and name_b.startswith("CCTV-"):
        return name_a == name_b

    # 名称相似度 > 0.85 视为同一频道
    if similar(name_a, name_b) > 0.85:
        return True

    return False


# -----------------------------------
# 选择最优源（增强版）
# -----------------------------------
def choose_best(a, b):
    """
    选择更好的频道源：
    1. HTTP > RTMP > UDP
    2. 清晰度优先（4K > 1080P > 720P > SD）
    3. 速度优先（speed 字段）
    """

    # 1. 协议优先级
    def protocol_score(url):
        if url.startswith("http"):
            return 3
        if url.startswith("rtmp"):
            return 2
        if url.startswith("udp"):
            return 1
        return 0

    pa = protocol_score(a["url"])
    pb = protocol_score(b["url"])
    if pa != pb:
        return a if pa > pb else b

    # 2. 清晰度优先（使用 quality_detector 的结果）
    quality_rank = {"4K": 4, "1080P": 3, "720P": 2, "SD": 1}

    qa = quality_rank.get(a.get("quality", "SD"), 1)
    qb = quality_rank.get(b.get("quality", "SD"), 1)
    if qa != qb:
        return a if qa > qb else b

    # 3. 速度优先
    sa = a.get("speed", 0)
    sb = b.get("speed", 0)
    if sa != sb:
        return a if sa > sb else b

    # 默认保留第一个
    return a


# -----------------------------------
# 主入口：智能去重（增强版）
# -----------------------------------
def run(channels):
    result = []

    for ch in channels:
        # URL 归一化
        ch["url"] = normalize_url(ch["url"])

        merged = False

        for i, exist in enumerate(result):
            if is_same_channel(ch, exist):
                # 选择更优源
                result[i] = choose_best(ch, exist)
                merged = True
                break

        if not merged:
            result.append(ch)

    return result
