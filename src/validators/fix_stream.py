import aiohttp
import asyncio
from utils.logger import logger

MAX_CONCURRENCY = 50
TIMEOUT = 2

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Referer": "https://www.google.com/",
    "Origin": "https://www.google.com",
    "Accept": "*/*",
}

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
    text = await fetch_text(session, url)
    if not text:
        return url

    if "#EXT-X-STREAM-INF" in text:
        lines = text.splitlines()
        subs = [l.strip() for l in lines if l.endswith(".m3u8")]

        if subs:
            sub = subs[0]
            if not sub.startswith("http"):
                base = url.rsplit("/", 1)[0]
                sub = f"{base}/{sub}"
            return sub

    return url

async def fix_channel(session, ch):
    url = ch["url"]

    if not url.startswith("http"):
        return ch

    ch["url"] = await fix_hls(session, url)
    return ch

async def run_all(channels):
    async with aiohttp.ClientSession() as session:
        tasks = [fix_channel(session, ch) for ch in channels]
        fixed = await asyncio.gather(*tasks)

    logger.info("[fix_stream] 已自动修复 HLS/Headers")
    return fixed

def run(channels):
    return asyncio.run(run_all(channels))
