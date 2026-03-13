GROUP_ORDER = {
    "CCTV": 1,
    "卫视": 2,
    "地方": 3,
    "影视": 4,
    "体育": 5,
    "其他": 9
}

def run(channels):
    return sorted(
        channels,
        key=lambda ch: (
            GROUP_ORDER.get(ch["group"], 99),
            ch["name"]
        )
    )
