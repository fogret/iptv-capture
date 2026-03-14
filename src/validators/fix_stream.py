import aiohttp
import asyncio
import re
from utils.logger import logger

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Referer": "https://www.google.com/",
    "Origin": "https://www.google.com",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
}

MAX_CONCURRENCY = 50
TIMEOUT = 2
sem = asyncio.Semaphore(MAX_CONCURRENCY)


async def fetch_text(session, url):
    try:
        async with sem:
            async with session.get(url, headers=DEFAULT_HEADERS, timeout=TIMEOUT) as resp:
                if resp.status >= 500:
                    return None
                return await resp.text()
    except:
        return None


async def fix_hls(session, url):
    """
    自动修复 HLS：
    1. 访问主 m3u8
    2. 如果是多码率，自动选择最高码率子 m3u8
    3. 返回最终可播 URL
    """
    text = await fetch_text(session, url)
    if not text:
        return url  # 无法修复

    # 多码率 m3u8
    if "#EXT-X-STREAM-INF" in text:
        lines = text.splitlines()
        sub_urls = [l.strip() for l in lines if l.endswith(".m3u8")]

        if sub_urls:
            # 自动选择第一个（通常是最高码率）
            sub = sub_urls[0]
            if not sub.startswith("http"):
                base = url.rsplit("/", 1)[0]
                sub = f"{base}/{sub}"
            return sub

    return url


async def fix_channel(session, ch):
    url = ch["url"]

    # 只修复 http/hls
    if not url.startswith("http"):
        return ch

    # 自动修复 HLS
    fixed = await fix_hls(session, url)
    ch["url"] = fixed

    return ch


async def run_all(channels):
    async with aiohttp.ClientSession() as session:
        tasks = [fix_channel(session, ch) for ch in channels]
        fixed = await asyncio.gather(*tasks)

    logger.info("[fix_stream] 已自动修复 HLS/Headers")
    return fixed


def run(channels):
    return asyncio.run(run_all(channels))
