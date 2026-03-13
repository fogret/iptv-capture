from epg.epg_fetcher import fetch_epg
from epg.epg_generator import generate_epg
from processors.logo_mapper import run as map_logo
from processors.filter_quality import run as filter_quality
from collectors.public_lists import collect as collect_public
from collectors.custom_sources import collect as collect_custom
from validators.http_checker import check as check_http
from processors.normalize_name import run as normalize
from processors.deduplicate import run as dedup
from processors.classify import run as classify
from exporters.m3u_exporter import export_m3u
from exporters.json_exporter import export_tvbox
from utils.config_loader import load_config
from utils.logger import logger
from validators.speed_tester import check as speed_test

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

    # 6. EPG generation
    xml_data = fetch_epg()
    generate_epg(xml_data, channels)
    
    # 7. Logo mapping
    channels = map_logo(channels)
    
    # 8. Deduplicate
    channels = dedup(channels)

    # 9. Classify
    channels = classify(channels)

    # 10. Export
    cfg = load_config()
    export_m3u(channels, cfg["export"]["m3u_path"])
    export_tvbox(channels, cfg["export"]["tvbox_json_path"])

    logger.info("=== IPTV Capture Done ===")

if __name__ == "__main__":
    main()
