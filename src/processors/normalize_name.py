import re

# -------------------------------
# Level 1：基础清洗
# -------------------------------
def normalize_basic(name: str) -> str:
    """
    基础清洗：
    - 去除空格
    - 去除多余符号
    - 去除常见无意义后缀（高清、HD、频道、台）
    """
    if not name:
        return ""

    n = name.strip()

    # 去掉常见无意义后缀
    n = re.sub(r"(高清|HD|频道|台)$", "", n, flags=re.IGNORECASE)

    # 去掉多余空格
    n = re.sub(r"\s+", "", n)

    return n


# -------------------------------
# Level 2：智能标准化
# -------------------------------
def normalize_advanced(name: str) -> str:
    """
    智能标准化：
    - CCTV 标准化（CCTV-1 / CCTV-5+）
    - 卫视标准化（湖南卫视 / 浙江卫视）
    - 地方台常见清洗
    """
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
# Level 3：自动分类
# -------------------------------
def classify(name: str) -> str:
    """
    自动分类：
    - 央视
    - 卫视
    - 体育
    - 电影
    - 地方台（默认）
    """
    upper = name.upper()

    if "CCTV" in upper:
        return "央视"

    if "卫视" in name:
        return "卫视"

    if "体育" in name or "SPORT" in upper:
        return "体育"

    if "电影" in name:
        return "电影"

    return "地方"


# -------------------------------
# 主入口：run(channels)
# -------------------------------
def run(channels):
    """
    统一处理流程：
    1. 基础清洗
    2. 智能标准化
    3. 自动分类
    """
    for ch in channels:
        if "name" in ch:
            # Level 1
            ch["name"] = normalize_basic(ch["name"])

            # Level 2
            ch["name"] = normalize_advanced(ch["name"])

            # Level 3
            ch["group"] = classify(ch["name"])

    return channels
