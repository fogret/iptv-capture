import json
import os
from utils.logger import logger

def export_web_data(channels, path="output/web/data/channels.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)
    logger.info(f"[web_exporter] Web data exported: {path}")


def export_web_pages():
    os.makedirs("output/web", exist_ok=True)

    # index.html
    index_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>IPTV Web UI</title>
<style>
body { font-family: Arial; background: #f5f5f5; }
.channel { display: flex; align-items: center; padding: 8px; background: #fff; margin: 6px; border-radius: 6px; }
.logo { width: 60px; height: 60px; margin-right: 10px; }
.group { font-weight: bold; margin-top: 20px; font-size: 20px; }
.status-ok { color: green; }
.status-bad { color: red; }
</style>
</head>
<body>
<h1>IPTV Web UI</h1>
<div id="content">加载中...</div>

<script>
fetch("data/channels.json")
  .then(r => r.json())
  .then(chs => {
    let html = "";
    let groups = {};

    chs.forEach(ch => {
      if (!groups[ch.group]) groups[ch.group] = [];
      groups[ch.group].push(ch);
    });

    for (let g in groups) {
      html += `<div class='group'>${g}</div>`;
      groups[g].forEach(ch => {
        let status = ch.ok || ch.udp_ok ? "status-ok" : "status-bad";
        html += `
          <div class='channel'>
            <img class='logo' src='${ch.logo || ""}' />
            <div>
              <div>${ch.name}</div>
              <div class='${status}'>${ch.ok || ch.udp_ok ? "可用" : "不可用"}</div>
              <a href='player.html?url=${encodeURIComponent(ch.url)}' target='_blank'>播放</a>
            </div>
          </div>
        `;
      });
    }

    document.getElementById("content").innerHTML = html;
  });
</script>
</body>
</html>
"""
    with open("output/web/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    # player.html
    player_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>播放</title>
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
</head>
<body>
<video id="video" controls autoplay style="width:100%;max-width:800px;"></video>

<script>
const url = new URLSearchParams(location.search).get("url");
const video = document.getElementById("video");

if (Hls.isSupported()) {
  const hls = new Hls();
  hls.loadSource(url);
  hls.attachMedia(video);
} else {
  video.src = url;
}
</script>
</body>
</html>
"""
    with open("output/web/player.html", "w", encoding="utf-8") as f:
        f.write(player_html)

    logger.info("[web_exporter] Web UI pages generated.")
