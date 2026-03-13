import re

def normalize_name(name: str) -> str:
    """
    对频道名称进行标准化处理：
    - 去除空格
    - 去除多余符号
    - 统一大小写格式
    - 去除常见无意义后缀（高清、HD、频道等）
    """
    if not name:
        return ""

    n = name.strip()

    # 去掉常见无意义后缀
    n = re.sub(r"(高清|HD|频道|台)$", "", n, flags=re.IGNORECASE)

    # 去掉多余空格
    n = re.sub(r"\s+", "", n)

    return n

def run(channels):
    """
    对频道列表中的 name 字段进行标准化
    """
    for ch in channels:
        if "name" in ch:
            ch["name"] = normalize_name(ch["name"])
    return channels
