import requests
from utils.logger import logger

# 国内频道关键词
DOMESTIC_KEYWORDS = [
    "CCTV", "卫视", "贵州", "北京", "上海", "广东", "湖南",
    "东方", "浙江", "江苏", "深圳", "四川", "重庆", "安徽",
    "山东", "黑龙江", "吉林", "辽宁", "河北", "河南", "湖北",
    "江西", "福建", "广西", "云南", "海南", "内蒙古", "宁夏",
    "青海", "甘肃", "西藏", "新疆", "都市", "公共", "影视", "新闻", "体育"
]

# 国外频道关键词（用于过滤）
FOREIGN_KEYWORDS = [
    "HBO", "BBC", "CNN", "NHK", "FOX", "SKY", "KBS", "MBC",
    "JAPAN", "KOREA", "USA", "UK", "FRANCE", "GERMAN"
]

# 国内 M3U 源
M3U_LISTS = [
    "https://raw.githubusercontent.com/fanmingming/live/main/tv/m3u/China.m3u",
    "https://raw.githubusercontent.com/YanG-1989/m3u/main/TV.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/cn.m3u"
]

def is_domestic(name):
    name = name.upper()
    return any(k in name for k in DOMESTIC_KEYWORDS) and \
           not any(k in name for k in FOREIGN_KEYWORDS)

def collect():
    channels = []

    for url in M3U_LISTS:
        logger.info(f"[public_cn] Fetching: {url}")
        try:
            text = requests.get(url, timeout=10).text
            channels.extend(parse_m3u(text))
        except Exception as e:
            logger.error(f"[public_cn] Failed: {e}")

    return channels

def parse_m3u(text):
    result = []
    lines = text.splitlines()

    name = None
    logo = None
    group = None

    for line in lines:
        line = line.strip()

        if line.startswith("#EXTINF"):
            name = extract(line, "tvg-name") or extract(line, "group-title") or "未知频道"
            logo = extract(line, "tvg-logo")

            # 自动分类
            if "CCTV" in name.upper():
                group = "央视"
            elif "卫视" in name:
                group = "卫视"
            else:
                group = "地方"

        elif line.startswith("http"):
            if is_domestic(name):
                result.append({
                    "name": name,
                    "url": line,
                    "logo": logo,
                    "group": group
                })

    return result

def extract(line, key):
    if key + '="' in line:
        return line.split(key + '="')[1].split('"')[0]
    return None
