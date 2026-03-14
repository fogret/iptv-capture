import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.append(SRC_DIR)

from utils.logger import logger

logger.info(f">>> 当前工作目录: {os.getcwd()}")
logger.info(">>> 正在运行最新 main.py <<<")

from exporters.monitor_exporter import export_monitor_ui
from exporters.api_exporter import export_channels, export_groups, export_status, export_search_api
from exporters.web_exporter import export_web_data, export_web_pages
from exporters.tvbox_category_exporter import export_tvbox_categories
from exporters.m3u_exporter import export_m3u
from exporters.json_exporter import export_tvbox

from collectors.udp_sources import collect as collect_udp
from collectors.public_lists import collect as collect_public
from collectors.custom_sources import collect as collect_custom
from collectors.public_cn_sources import collect as collect_cn

from validators.http_checker import check as check_http
from validators.udp_checker import check as check_udp
from validators.speed_tester import check as speed_test

from processors.sort_channels import run as sort_channels
from processors.normalize_name import run as normalize
from processors.filter_quality import run as filter_quality
from processors.logo_mapper import run as map_logo
from processors.deduplicate import run as dedup

from epg.epg_fetcher import fetch_epg
from epg.epg_generator import generate_epg
from epg.epg_mapper import epg_map

from utils.config_loader import load_config


def main():
    cfg = load_config()
    logger.info(f">>> config.json 内容: {cfg}")
    
    # 1. Collect
    channels = []
    channels += collect_public()
    channels += collect_custom()
    channels += collect_cn()
    channels += collect_udp()

    # 2. Normalize（含自动分组）
    channels = normalize(channels)

    # 3. Validate
    channels = check_http(channels)
    channels = check_udp(channels)
    channels = speed_test(channels)

    # 4. EPG mapping
    channels = epg_map(channels)

    # 5. Quality filter
    cfg = load_config()
    channels = filter_quality(channels, cfg.get("quality_filter"))

    # 6. Logo mapping
    channels = map_logo(channels)

    # 7. EPG generation
    xml_data = fetch_epg()
    generate_epg(xml_data, channels)

    # 8. TVBox categories（按 group 自动分组）
    export_tvbox_categories(channels)

    # 9. Web UI
    export_web_data(channels)
    export_web_pages()

    # 10. API
    export_channels(channels)
    export_groups(channels)
    export_status(channels)
    export_search_api()

    # 11. Deduplicate
    channels = dedup(channels)

    # 12. Export
    cfg = load_config()
    export_m3u(channels, cfg["export"]["m3u_path"])
    export_tvbox(channels, cfg["export"]["tvbox_json_path"])

    # 13. Monitor
    export_monitor_ui()

    logger.info("=== IPTV Capture Done ===")


if __name__ == "__main__":
    main()
