import re
from processors.group_mapper import get_group

# -------------------------------
# Level 1：基础清洗
# -------------------------------
def normalize_basic(name: str) -> str:
    if not name:
        return ""

    n = name.strip()
    n = re.sub(r"(高清|HD|频道|台)$", "", n, flags=re.IGNORECASE)
    n = re.sub(r"\s+", "", n)
    return n


# -------------------------------
# Level 2：智能标准化
# -------------------------------
def normalize_advanced(name: str) -> str:
    if not name:
        return ""

    upper = name.upper()

    # CCTV 标准化
    if "CCTV" in upper:
        num = re.findall(r"\d+", upper)
        if num:
            return f"CCTV-{num[0]}"
        return "CCTV"

    # 卫视标准化
    if "卫视" in name:
        return name.replace("高清", "").replace("HD", "").strip()

    # 地方台常见清洗
    n = name.replace("高清", "").replace("HD", "").replace("频道", "").strip()
    return n


# -------------------------------
# 主入口：run(channels)
# -------------------------------
def run(channels):
    for ch in channels:
        if "name" in ch:
            ch["name"] = normalize_basic(ch["name"])
            ch["name"] = normalize_advanced(ch["name"])
            ch["group"] = get_group(ch["name"])   # 自动分组
    return channels
