def run(channels):
    """
    自动排序：
    1. 按 group 优先级排序
    2. 组内按频道名排序
    3. CCTV 特殊排序（CCTV-1 → CCTV-2 → CCTV-3…）
    """

    # -------------------------------
    # 1. group 优先级
    # -------------------------------
    group_priority = {
        "央视": 1,
        "卫视": 2,
        "地方": 3,
        "体育": 4,
        "电影": 5,
        "纪录片": 6,
        "少儿": 7,
        "港澳台": 8,
        "国际台": 9,
        "购物": 10,
        "轮播": 11,
        "直播": 12,
        "组播": 13,
        "其他": 99
    }

    def group_key(ch):
        group = ch.get("group", "其他")
        return group_priority.get(group, 99)

    # -------------------------------
    # 2. CCTV 特殊排序
    # -------------------------------
    def cctv_key(name):
        if name.startswith("CCTV-"):
            try:
                return int(name.split("-")[1])
            except:
                return 999
        return 999

    # -------------------------------
    # 3. 组内排序：CCTV → 数字 → 字典序
    # -------------------------------
    def name_key(ch):
        name = ch.get("name", "")
        return (
            cctv_key(name),  # CCTV-1 → CCTV-2 → CCTV-3
            name             # 其他按字典序
        )

    # -------------------------------
    # 最终排序
    # -------------------------------
    channels.sort(key=lambda ch: (group_key(ch), name_key(ch)))

    return channels
