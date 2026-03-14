PROVINCES = ["北京", "上海", "广东", "江苏", "浙江", "山东", "四川", "湖北", "湖南", "福建", "河北", "河南", "安徽", "江西", "广西", "云南", "贵州", "陕西", "山西", "黑龙江", "吉林", "辽宁", "内蒙古", "宁夏", "青海", "甘肃", "新疆", "西藏", "海南"]

def detect_region(name):
    for p in PROVINCES:
        if p in name:
            return p
    return "未知地区"


def run(channels):
    for ch in channels:
        ch["region"] = detect_region(ch["name"])
    return channels
