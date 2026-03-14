import asyncio
import aiohttp
from utils.logger import logger

MAX_CONCURRENCY = 50
TIMEOUT = 2

# 删除 UA / Referer / Origin / Accept，只保留空 headers
DEFAULT_HEADERS = {}

sem = asyncio.Semaphore(MAX_CONCURRENCY)

async def test_playable(session, url):
    try:
        async with sem:
            async with session.get(url, headers=DEFAULT_HEADERS, timeout=TIMEOUT) as resp:
                return resp.status < 500
    except:
        return False

async def run_all(channels):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for ch in channels:
            if ch["url"].startswith("http"):
                tasks.append(test_playable(session, ch["url"]))
            else:
                tasks.append(asyncio.sleep(0, result=True))

        results = await asyncio.gather(*tasks)

    valid = []
    for ch, ok in zip(channels, results):
        if ok:
            valid.append(ch)

    logger.info(f"[playable_checker] 可播放频道: {len(valid)} / {len(channels)}")
    return valid

def check(channels):
    return asyncio.run(run_all(channels))
