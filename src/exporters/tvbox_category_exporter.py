import json
import os
from utils.logger import logger

def build_structure(channels):
    result = {}

    for ch in channels:
        group = ch["group"] or "其他"

        # 二级分类（地方台按省份）
        subgroup = None
        if group == "地方":
            # 例如：贵州-1 → 贵州
            name = ch["name"]
            if "-" in name:
                subgroup = name.split("-")[0]
            else:
                subgroup = "其他地方台"

        if group not in result:
            result[group] = {}

        if subgroup:
            if subgroup not in result[group]:
                result[group][subgroup] = []
            result[group][subgroup].append(ch)
        else:
            if "default" not in result[group]:
                result[group]["default"] = []
            result[group]["default"].append(ch)

    return result


def export_tvbox_categories(channels, output_path="output/tvbox_channels.json"):
    logger.info("[tvbox_category_exporter] Generating TVBox category JSON...")

    structure = build_structure(channels)

    final = []

    for group, subgroups in structure.items():
        group_item = {
            "name": group,
            "channels": []
        }

        for subgroup, ch_list in subgroups.items():
            if subgroup == "default":
                # 一级分类直接放频道
                for ch in ch_list:
                    group_item["channels"].append({
                        "name": ch["name"],
                        "url": ch["url"],
                        "logo": ch.get("logo"),
                        "tvg_id": ch.get("tvg_id")
                    })
            else:
                # 二级分类
                subgroup_item = {
                    "name": subgroup,
                    "channels": []
                }
                for ch in ch_list:
                    subgroup_item["channels"].append({
                        "name": ch["name"],
                        "url": ch["url"],
                        "logo": ch.get("logo"),
                        "tvg_id": ch.get("tvg_id")
                    })
                group_item["channels"].append(subgroup_item)

        final.append(group_item)

    os.makedirs("output", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    logger.info(f"[tvbox_category_exporter] Done: {output_path}")
