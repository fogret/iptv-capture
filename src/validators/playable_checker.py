import asyncio
import aiohttp
from utils.logger import logger

MAX_CONCURRENCY = 100
TIMEOUT = 5

async def test_playable(session, url):
    try:
        async with session.get(url, timeout=TIMEOUT) as resp:
            text = await resp.text()

            # HLS playlist 必须包含 #EXTINF
            if "#EXTINF" in text:
                return True

            # TS 流必须能读到数据
            data = await resp.content.read(1024)
            if len(data) > 0:
                return True

    except:
        return False

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
