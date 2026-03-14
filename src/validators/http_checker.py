import asyncio
import aiohttp
import hashlib
import os
import json
from utils.logger import logger

MAX_CONCURRENCY = 200
TIMEOUT = 2
RETRY = 1

CACHE_DIR = "data"
CACHE_FILE = os.path.join(CACHE_DIR, "http_cache.json")

# 自动创建 data/ 目录
os.makedirs(CACHE_DIR, exist_ok=True)


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            return json.load(open(CACHE_FILE, "r", encoding="utf-8"))
        except:
            return {}
    return {}


def save_cache(cache):
    json.dump(cache, open(CACHE_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)


def url_hash(url):
    return hashlib.md5(url.encode()).hexdigest()


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
    cache = load_cache()

    async with aiohttp.ClientSession() as session:
        tasks = []
        urls = []

        for ch in channels:
            url = ch["url"]

            if not url.startswith("http"):
                tasks.append(asyncio.sleep(0, result=True))
                urls.append(url)
                continue

            h = url_hash(url)
            if h in cache:
                tasks.append(asyncio.sleep(0, result=cache[h]))
                urls.append(url)
                continue

            tasks.append(fetch(session, url))
            urls.append(url)

        results = await asyncio.gather(*tasks)

    valid = []
    for ch, ok in zip(channels, results):
        h = url_hash(ch["url"])
        cache[h] = ok
        if ok:
            valid.append(ch)

    save_cache(cache)
    logger.info(f"[http_checker] {len(channels)} → {len(valid)}")
    return valid


def check(channels):
    return asyncio.run(check_all(channels))
