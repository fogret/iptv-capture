import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.exporters.monitor_exporter import export_monitor_ui
from src.exporters.api_exporter import export_channels, export_groups, export_status, export_search_api
from src.exporters.web_exporter import export_web_data, export_web_pages
from src.exporters.tvbox_category_exporter import export_tvbox_categories
from src.epg.epg_fetcher import fetch_epg
from src.epg.epg_generator import generate_epg
from src.processors.logo_mapper import run as map_logo
from src.processors.filter_quality import run as filter_quality
from src.collectors.public_lists import collect as collect_public
from src.collectors.custom_sources import collect as collect_custom
from src.validators.http_checker import check as check_http
from src.validators.udp_checker import check as check_udp
from src.processors.normalize_name import run as normalize
from src.processors.deduplicate import run as dedup
from src.processors.classify import run as classify
from src.exporters.m3u_exporter import export_m3u
from src.exporters.json_exporter import export_tvbox
from src.utils.config_loader import load_config
from src.utils.logger import logger
from src.validators.speed_tester import check as speed_test
from src.epg.epg_mapper import epg_map

def main():
    logger.info("=== IPTV Capture Start ===")

    # 1. Collect
    channels = []
    channels += collect_public()
    channels += collect_custom()

    # 2. Normalize
    channels = normalize(channels)

    # 3. Validate (HTTP + UDP + Speed)
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

    # 8. TVBox category JSON
    export_tvbox_categories(channels)

    # 9. Web UI export
    export_web_data(channels)
    export_web_pages()

    # 10. API export
    export_channels(channels)
    export_groups(channels)
    export_status(channels)
    export_search_api()

    # 11. Deduplicate
    channels = dedup(channels)

    # 12. Classify
    channels = classify(channels)

    # 13. Export
    cfg = load_config()
    export_m3u(channels, cfg["export"]["m3u_path"])
    export_tvbox(channels, cfg["export"]["tvbox_json_path"])

    # 14. Monitor Dashboard
    export_monitor_ui()  

logger.info("=== IPTV Capture Done ===")

if __name__ == "__main__":
    main()
