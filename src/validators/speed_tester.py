import asyncio
import aiohttp
from utils.logger import logger

MAX_CONCURRENCY = 100
TIMEOUT = 2
TEST_SIZE = 1024 * 50  # 50KB


async def test_speed(session, url):
    try:
        async with session.get(url, timeout=TIMEOUT) as resp:
            data = await resp.content.read(TEST_SIZE)
            return len(data)
    except:
        return 0


async def run_all(channels):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for ch in channels:
            if ch["url"].startswith("http"):
                tasks.append(test_speed(session, ch["url"]))
            else:
                tasks.append(asyncio.sleep(0, result=0))

        speeds = await asyncio.gather(*tasks)

    for ch, sp in zip(channels, speeds):
        ch["speed"] = sp

    logger.info("[speed_tester] 完成测速")
    return channels


def check(channels):
    return asyncio.run(run_all(channels))
