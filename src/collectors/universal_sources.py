import os
from utils.logger import logger

# 旧 TXT + 网站抓取
from .public_lists import collect as collect_public_lists

# 未来你可以继续加其它 collector：
# from .udp_sources import collect as collect_udp
# from .isp_multicast import collect as collect_isp
# from .custom_sources import collect as collect_custom


def collect():
    channels = []

    logger.info("[universal_sources] 开始汇总所有来源")

    # 1. TXT + 网站抓取（public_lists 内部已整合 collect_websites）
    public_channels = collect_public_lists()
    channels.extend(public_channels)
    logger.info(f"[universal_sources] public_lists: {len(public_channels)} 条")

    # 2. 如果你以后要加其它 collector，在这里继续加：
    # udp_channels = collect_udp()
    # channels.extend(udp_channels)
    # logger.info(f"[universal_sources] udp_sources: {len(udp_channels)} 条")

    # isp_channels = collect_isp()
    # channels.extend(isp_channels)
    # logger.info(f"[universal_sources] isp_multicast: {len(isp_channels)} 条")

    # custom_channels = collect_custom()
    # channels.extend(custom_channels)
    # logger.info(f"[universal_sources] custom_sources: {len(custom_channels)} 条")

    logger.info(f"[universal_sources] 汇总完成，共 {len(channels)} 条频道")
    return channels
