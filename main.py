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

    # 3. Validate
    channels = check_http(channels)

    # 4. Deduplicate
    channels = dedup(channels)

    # 5. Classify
    channels = classify(channels)

    # 6. Export
    cfg = load_config()
    export_m3u(channels, cfg["export"]["m3u_path"])
    export_tvbox(channels, cfg["export"]["tvbox_json_path"])

    logger.info("=== IPTV Capture Done ===")

if __name__ == "__main__":
    main()
