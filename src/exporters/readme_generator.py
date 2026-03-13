from datetime import datetime

def generate_readme(channels, path):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    total = len(channels)

    content = f"""# IPTV Live

自动更新的 IPTV 直播源列表  
更新时间：**{now}**  
频道总数：**{total}**

## 订阅地址

- M3U: `https://raw.githubusercontent.com/yourname/iptv-capture/main/output/live.m3u`
- TVBox JSON: `https://raw.githubusercontent.com/yourname/iptv-capture/main/output/live_tvbox.json`

## 功能

- 自动抓取公开 IPTV 列表  
- 自动解析 m3u  
- 自动检测可用性（HTTP + UDP）  
- 自动去重  
- 自动分类  
- 自动排序  
- 自动生成 TVBox JSON  
- 自动生成 README  
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
