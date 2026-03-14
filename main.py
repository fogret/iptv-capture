import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.append(SRC_DIR)

from utils.logger import logger
from utils.config_loader import load_config

# Collectors
from collectors.universal_sources import collect as collect_sources

# Validators
from validators.http_checker import check as check_http
from validators.udp_checker import check as check_udp
from validators.speed_tester import check as speed_test
from validators.playable_checker import check as check_playable
from validators.fix_stream import run as fix_stream

# Processors
from processors.normalize_name import run as normalize
from processors.quality_detector import run as detect_quality
from processors.type_detector import run as detect_type
from processors.region_detector import run as detect_region
from processors.deduplicate import run as dedup
from processors.filter_quality import run as filter_quality
from processors.logo_mapper import run as map_logo
from processors.score_channels import run as score_channels
from processors.monitor_channels import run as monitor_channels
from processors.disable_channels import run as disable_channels
from processors.recover_channels import run as recover_channels
from processors.sort_channels import run as sort_channels

# EPG
from epg.epg_fetcher import fetch_epg
from epg.epg_generator import generate_epg
from epg.epg_mapper import epg_map

# Exporters
from exporters.m3u_exporter import export_m3u
from exporters.json_exporter import export_tvbox
from exporters.txt_exporter import export_txt
from exporters.web_exporter import export_web_data, export_web_pages
from exporters.api_exporter import (
    export_channels,
    export_groups,
    export_status,
    export_search_api,
)
from exporters.monitor_exporter import export_monitor_ui


def main():
    logger.info(">>> IPTV Capture System Started <<<")

    cfg = load_config()
    logger.info(f"Loaded config: {cfg}")

    # 1. Collect sources
    channels = collect_sources()
    logger.info(f"Collected {len(channels)} channels")

    # 2. Normalize names
    channels = normalize(channels)

    # 3. Auto-detect metadata
    channels = detect_quality(channels)
    channels = detect_type(channels)
    channels = detect_region(channels)

    # 4. Validators
    channels = check_http(channels)
    channels = check_udp(channels)
    channels = speed_test(channels)

    # 5. Fix streams (HLS 修复 + fallback)
    channels = fix_stream(channels)

    # 6. Playable check (温和过滤)
    channels = check_playable(channels)

    # 7. EPG mapping
    channels = epg_map(channels)

    # 8. Quality filter
    channels = filter_quality(channels, cfg.get("quality_filter"))

    # 9. Logo mapping
    channels = map_logo(channels)

    # 10. Fetch + generate EPG
    xml_data = fetch_epg()
    generate_epg(xml_data, channels)

    # 11. Deduplicate
    channels = dedup(channels)

    # 12. Score channels
    channels = score_channels(channels)

    # 13. Monitor (只累积 fail_count)
    channels = monitor_channels(channels)

    # 14. Disable (连续 3 次失败才禁用)
    channels = disable_channels(channels)

    # 15. Recover (状态恢复自动恢复)
    channels = recover_channels(channels)

    # 16. Sort channels
    channels = sort_channels(channels)

    # 17. Export M3U / JSON / TXT
    export_m3u(channels, cfg["export"]["m3u_path"])
    export_tvbox(channels, cfg["export"]["tvbox_json_path"])
    export_txt(channels, cfg["export"]["txt_path"])

    # 18. Export Web UI
    export_web_data(channels)
    export_web_pages()

    # 19. Export API
    export_channels(channels)
    export_groups(channels)
    export_status(channels)
    export_search_api()

    # 20. Export Monitor UI
    export_monitor_ui()

    logger.info(">>> IPTV Capture Completed <<<")


if __name__ == "__main__":
    main()
