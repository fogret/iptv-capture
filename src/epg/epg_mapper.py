def epg_map(channels):
    for ch in channels:
        name = ch.get("name", "")

        # CCTV
        if name.startswith("CCTV-"):
            num = name.split("-")[1]
            ch["epg_id"] = f"cctv{num}.cn"

        # 卫视
        elif "卫视" in name:
            ch["epg_id"] = f"{name}.cn"

        # 地方台 fallback
        else:
            ch["epg_id"] = name

    return channels
