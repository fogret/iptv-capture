def get_group(name: str) -> str:
    upper = name.upper()

    # 央视
    if upper.startswith("CCTV-"):
        return "央视"

    # 卫视
    if "卫视" in name:
        return "卫视"

    # 体育
    if "体育" in name or "SPORT" in upper:
        return "体育"

    # 电影
    if "电影" in name:
        return "电影"

    # 港澳台
    if any(x in name for x in ["香港", "澳门", "台湾", "TVB", "凤凰"]):
        return "港澳台"

    # 国际台
    if any(x in upper for x in ["HBO", "BBC", "CNN", "NHK", "FOX"]):
        return "国际台"

    # 少儿
    if any(x in name for x in ["少儿", "卡通", "动漫"]):
        return "少儿"

    # 纪录片
    if any(x in name for x in ["纪录", "探索", "地理"]):
        return "纪录片"

    # 购物
    if "购物" in name:
        return "购物"

    # 轮播
    if "轮播" in name:
        return "轮播"

    # 组播（UDP）
    if name.startswith("组播 "):
        return "组播"

    # 默认地方台
    return "地方"
