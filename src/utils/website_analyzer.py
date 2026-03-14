import os
import json
from datetime import datetime

def analyze_websites(stats, output_dir="output"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    analysis = {}

    for site, detail in stats.website_detail.items():
        entry = {
            "pages": detail["pages"],
            "max_depth": detail["max_depth"],
            "streams_found": len(detail["channels"]),
            "ads_blocked": len(detail["ads_blocked"]),
            "stream_types": [],
            "errors": []
        }

        # 统计流类型
        types = set()
        for ch in detail["channels"]:
            url = ch["url"].lower()
            if ".m3u8" in url:
                types.add("m3u8")
            elif ".flv" in url:
                types.add("flv")
            elif ".ts" in url:
                types.add("ts")
            elif "rtmp://" in url:
                types.add("rtmp")
        entry["stream_types"] = sorted(list(types))

        analysis[site] = entry

    # 保存 JSON
    json_path = os.path.join(output_dir, "website_analysis.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    # 保存 Markdown
    md_path = os.path.join(output_dir, "website_analysis.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# 网站抓取分析报告\n\n")
        f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for site, entry in analysis.items():
            f.write(f"## {site}\n")
            f.write(f"- 抓取页面数：{entry['pages']}\n")
            f.write(f"- 最大深度：{entry['max_depth']}\n")
            f.write(f"- 抓到直播流：{entry['streams_found']}\n")
            f.write(f"- 屏蔽广告：{entry['ads_blocked']}\n")
            f.write(f"- 流类型：{', '.join(entry['stream_types']) or '无'}\n")
            f.write("\n")

    return analysis
