import asyncio
import aiohttp
from utils.logger import logger

MAX_CONCURRENCY = 100
TIMEOUT = 2

async def test_playable(session, url):
    try:
        async with session.get(url, timeout=TIMEOUT) as resp:
            # 只要能访问成功就认为可播（温和过滤）
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
                tasks.append(asyncio.sleep(0, result=True))  # UDP 不测试

        results = await asyncio.gather(*tasks)

    valid = []
    for ch, ok in zip(channels, results):
        if ok:
            valid.append(ch)

    logger.info(f"[playable_checker] 可播放频道: {len(valid)} / {len(channels)}")
    return valid


def check(channels):
    return asyncio.run(run_all(channels))
