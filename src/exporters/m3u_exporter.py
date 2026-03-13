def export_m3u(channels, path):
    lines = ["#EXTM3U"]

    for ch in channels:
        line1 = f'#EXTINF:-1 tvg-id="{ch.get("tvg_id","")}" group-title="{ch["group"]}",{ch["name"]}'
        line2 = ch["url"]
        lines.append(line1)
        lines.append(line2)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
