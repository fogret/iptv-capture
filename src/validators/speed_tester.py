import asyncio
import aiohttp
from utils.logger import logger

MAX_CONCURRENCY = 50
TIMEOUT = 2
TEST_SIZE = 50000  # 50KB

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

async def test_speed(session, ch):
    url = ch["url"]

    if not url.startswith("http"):
        ch["speed"] = 0
        return ch

    try:
        async with sem:
            async with session.get(url, headers=DEFAULT_HEADERS, timeout=TIMEOUT) as resp:
                data = await resp.content.read(TEST_SIZE)
                ch["speed"] = len(data)
                return ch
    except:
        ch["speed"] = 0
        return ch

async def run_all(channels):
    async with aiohttp.ClientSession() as session:
        tasks = [test_speed(session, ch) for ch in channels]
        return await asyncio.gather(*tasks)

def check(channels):
    logger.info("[speed_tester] 开始测速")
    return asyncio.run(run_all(channels))
