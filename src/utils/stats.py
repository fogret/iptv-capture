# src/utils/stats.py

class Stats:
    def __init__(self):
        # 按来源统计（从最终 channels 里按 origin 反推）
        self.total_collected = 0

        # 网站抓取全局统计
        self.website_pages_total = 0
        self.website_max_depth_global = 0
        self.website_ads_blocked_total = 0

        # 网站级明细：{ root_url: { pages, max_depth, channels[], ads_blocked[] } }
        self.website_detail = {}


stats = Stats()
