import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.append(SRC_DIR)

from utils.logger import logger

logger.info(f">>> 当前工作目录: {os.getcwd()}")
logger.info(">>> 正在运行最新 main.py <<<")

# ============================
# Exporters
# ============================
from exporters.monitor_exporter import export_monitor_ui
from exporters.api_exporter import export_channels, export_groups, export_status, export_search_api
from exporters.web_exporter import export_web_data, export_web_pages
from exporters.tvbox_category_exporter import export_tvbox_categories
from exporters.m3u_exporter import export_m3u
from exporters.json_exporter import export_tvbox

# ============================
# Collectors（万能采集器）
# ============================
from collectors.universal_sources import collect as collect_sources

# ============================
# Validators
# ============================
from validators.http_checker import check as check_http
from validators.udp_checker import check as check_udp
from validators.speed_tester import check as speed_test
from validators.playable_checker import check as check_playable

# ============================
# Processors
# ============================
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

# ============================
# EPG
# ============================
from epg.epg_fetcher import fetch_epg
from epg.epg_generator import generate_epg
from epg.epg_mapper import epg_map

# ============================
# Config
# ============================
from utils.config_loader import load_config


def main():
    cfg = load_config()
    logger.info(f">>> config.json 内容: {cfg}")
    
    # 1. Collect（sources/ 下所有 txt）
    channels = collect_sources()

    # 2. Normalize（名称规范化 + 基础分组）
    channels = normalize(channels)

    # 3. 自动识别：清晰度 / 类型 / 地区
    channels = detect_quality(channels)
    channels = detect_type(channels)
    channels = detect_region(channels)

    # 4. Validate（异步 HTTP + UDP + 异步测速）
    channels = check_http(channels)
    channels = check_udp(channels)
    channels = speed_test(channels)

    # 4.5 真实播放测试（只保留能真正播放的频道）
    channels = check_playable(channels)

    # 5. EPG mapping
    channels = epg_map(channels)

    # 6. Quality filter
    cfg = load_config()
    channels = filter_quality(channels, cfg.get("quality_filter"))

    # 7. Logo mapping
    channels = map_logo(channels)

    # 8. EPG generation
    xml_data = fetch_epg()
    generate_epg(xml_data, channels)

    # 9. Deduplicate（智能去重）
    channels = dedup(channels)

    # 10. Score
    channels = score_channels(channels)

    # 11. Monitor channels (评分下降报警 + 自动禁用)
    channels = monitor_channels(channels)

    # 12. Disable channels（自动禁用）
    channels = disable_channels(channels)
    
    # 13. Recover channels（自动恢复）
    channels = recover_channels(channels)
    
    # 14. Sort
    channels = sort_channels(channels)
    
    # 15. Export（M3U / TVBox）
    cfg = load_config()
    export_m3u(channels, cfg["export"]["m3u_path"])
    export_tvbox(channels, cfg["export"]["tvbox_json_path"])

    # 16. Web UI
    export_web_data(channels)
    export_web_pages()

    # 17. API
    export_channels(channels)
    export_groups(channels)
    export_status(channels)
    export_search_api()

    # 18. Monitor UI
    export_monitor_ui()

    logger.info("=== IPTV Capture Done ===")


if __name__ == "__main__":
    main()
