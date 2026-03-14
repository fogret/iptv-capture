import asyncio
import aiohttp
from utils.logger import logger

MAX_CONCURRENCY = 200   # 并发数，可调 100–500
TIMEOUT = 5             # 单个请求超时
RETRY = 1               # 重试次数

sem = asyncio.Semaphore(MAX_CONCURRENCY)


async def fetch(session, url):
    for _ in range(RETRY + 1):
        try:
            async with sem:
                async with session.get(url, timeout=TIMEOUT) as resp:
                    return resp.status < 500
        except:
            continue
    return False


async def check_all(channels):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for ch in channels:
            if ch["url"].startswith("http"):
                tasks.append(fetch(session, ch["url"]))
            else:
                tasks.append(asyncio.sleep(0, result=True))

        results = await asyncio.gather(*tasks)

    valid = []
    for ch, ok in zip(channels, results):
        if ok:
            valid.append(ch)

    logger.info(f"[http_checker] {len(channels)} → {len(valid)}")
    return valid


def check(channels):
    return asyncio.run(check_all(channels))
