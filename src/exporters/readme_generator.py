from datetime import datetime
from collections import Counter

def generate_readme(channels, path, stats):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    total = len(channels)

    # 分类统计
    groups = Counter([c.get("group", "未知") for c in channels])

    # 来源统计
    origins = Counter([c.get("origin", "unknown") for c in channels])

    # UA 统计
    ua_need = sum(1 for c in channels if c.get("need_ua"))
    ua_no = total - ua_need

    # HLS 深度解析统计
    hls_key = getattr(stats, "hls_key_total", 0)
    hls_ts = getattr(stats, "hls_ts_total", 0)
    hls_sub = getattr(stats, "hls_sub_m3u8_total", 0)

    # 网站抓取统计
    website_pages = getattr(stats, "website_pages_total", 0)
    website_ads = getattr(stats, "website_ads_blocked_total", 0)

    content = f"""# IPTV Live

自动更新的 IPTV 直播源列表  
更新时间：**{now}**  
频道总数：**{total}**

---

## 📡 订阅地址（自动更新）

- M3U: `https://raw.githubusercontent.com/fogret/iptv-custom/main/output/live.m3u`
- TVBox JSON: `https://raw.githubusercontent.com/fogret/iptv-custom/main/output/live_tvbox.json`

---

## 📊 频道分类统计

{"".join([f"- **{g}**：{n} 条\n" for g, n in groups.items()])}

---

## 🌍 来源统计

- 自定义源（custom）：**{origins.get('custom', 0)}**
- 公共源（public）：**{origins.get('public', 0)}**
- 网站抓取（website）：**{origins.get('website', 0)}**
- 其它：**{origins.get('unknown', 0)}**

---

## 🧠 智能 UA 统计

- 需要 UA：**{ua_need}**
- 不需要 UA：**{ua_no}**

---

## 🔍 HLS 深度解析统计

- 子 m3u8：**{hls_sub}**
- KEY：**{hls_key}**
- TS：**{hls_ts}**

---

## 🌐 网站抓取统计

- 抓取页面总数：**{website_pages}**
- 屏蔽广告链接：**{website_ads}**

---

## 🚀 项目功能（完整能力）

### 数据采集
- 网站全格式抓取（m3u8 / flv / mp4 / ts / mpd / f4m / rtmp / live?...）
- 自动解析 JS 播放器（DPlayer / CKPlayer / xgplayer / video.js）
- 自动解析 iframe 内嵌直播页面
- 自动解析 HLS（子 m3u8 / KEY / TS）
- 自动补全相对路径
- 自动抓取公开 IPTV 列表
- 自动解析本地 TXT / M3U / JSON 源

### 智能 UA 系统
- 自动识别 CDN（央视 / 电信 / 移动 / 阿里 / 腾讯）
- 自动识别格式（flv / f4m / m3u8 / ts / mp4）
- 自动识别播放器 UA（TVBox / PotPlayer / VLC / Android）
- 自动识别网页真实 UA / Referer / Cookie / Host
- 自动识别 HLS KEY / TS UA
- 自动 fallback（失败 → 自动加 UA）
- 自动缓存 UA 决策

### 数据清洗
- 自动检测可用性（HTTP + UDP）
- 自动测速（首包 / 速度 / 稳定性）
- 自动去重（URL + 频道名）
- 自动过滤广告源
- 自动过滤假源（404 / 403 / 500 / 假 m3u8 / 假 flv / 假直播）
- 自动清洗无效字段

### 输出
- 自动生成 M3U
- 自动生成 TVBox JSON
- 自动生成 TXT
- 自动生成 README
- 自动生成统计数据

---

## 📌 说明

本项目仅用于技术研究与学习，不提供任何商业用途。

"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
