import re
from bs4 import BeautifulSoup

# 拼音/简写 → 中文频道名映射
PINYIN_MAP = {
    "hunantv": "湖南卫视",
    "gdtv": "广东卫视",
    "gzstv": "贵州卫视",
    "jstv": "江苏卫视",
    "zjstv": "浙江卫视",
    "cctv": "CCTV",
}

# 清洗规则
CLEAN_PATTERNS = [
    r"直播",
    r"高清",
    r"HD",
    r"在线",
    r"观看",
    r"频道",
    r"Live",
]


def clean_name(name: str) -> str:
    for p in CLEAN_PATTERNS:
        name = re.sub(p, "", name, flags=re.IGNORECASE)
    return name.strip()


def extract_from_title(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
        if 2 <= len(title) <= 20:
            return clean_name(title)
    return None


def extract_from_headers(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in ["h1", "h2", "h3"]:
        for h in soup.find_all(tag):
            text = h.get_text(strip=True)
            if 2 <= len(text) <= 20:
                return clean_name(text)
    return None


def extract_from_images(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for img in soup.find_all("img"):
        for key in ["alt", "title"]:
            if img.get(key):
                text = img.get(key).strip()
                if 2 <= len(text) <= 20:
                    return clean_name(text)
    return None


def extract_from_json(html: str) -> str:
    m = re.search(r'"title"\s*:\s*"([^"]+)"', html)
    if m:
        return clean_name(m.group(1))
    return None


def extract_from_url(url: str) -> str:
    for key, name in PINYIN_MAP.items():
        if key in url.lower():
            return name
    m = re.search(r"(cctv\d+)", url.lower())
    if m:
        return m.group(1).upper()
    return None


def guess_channel_name(url: str, html: str) -> str:
    for extractor in [
        extract_from_title,
        extract_from_headers,
        extract_from_images,
        extract_from_json,
        extract_from_url,
    ]:
        name = extractor(html) if extractor != extract_from_url else extractor(url)
        if name:
            return name

    return "未知频道"
