import re

GROUP_KEYWORDS = {
    "央视": [
        r"cctv", r"中央", r"央视",
    ],
    "卫视": [
        r"卫视", r"tv$", r"tv[0-9]+",
    ],
    "新闻": [
        r"新闻", r"news", r"时政",
    ],
    "体育": [
        r"体育", r"sports", r"ball", r"football", r"nba",
    ],
    "影视": [
        r"影视", r"电影", r"影院", r"drama", r"movie",
    ],
    "都市": [
        r"都市", r"city", r"生活",
    ],
    "公共": [
        r"公共", r"民生", r"法治",
    ],
    "地方台": [
        r"tv", r"频道", r"综合", r"传媒", r"广播",
    ],
}

PLATFORM_GROUP = {
    "douyu.com": "直播平台",
    "huya.com": "直播平台",
    "bilibili.com": "直播平台",
}


def guess_group(name: str, url: str) -> str:
    url_l = url.lower()
    name_l = name.lower()

    # 直播平台
    for key, group in PLATFORM_GROUP.items():
        if key in url_l:
            return group

    # 关键词匹配（频道名 + URL）
    for group, patterns in GROUP_KEYWORDS.items():
        for p in patterns:
            if re.search(p, name_l) or re.search(p, url_l):
                return group

    # 默认 fallback
    return "其它"
