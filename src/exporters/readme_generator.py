并且每个条形图可以使用不同颜色，例如：

- 红色：央视  
- 黄色：卫视  
- 蓝色：地方台  
- 绿色：其它  

---

# ⭐ 最终版 generate_readme（彩色图表 + 排序 + 折叠 + 自动订阅地址）

```python
from datetime import datetime
from collections import Counter

# ANSI 颜色
COLOR_MAP = {
    "央视": "\033[91m",      # 红
    "卫视": "\033[93m",      # 黄
    "地方台": "\033[94m",    # 蓝
    "其它": "\033[92m",      # 绿
    "未知": "\033[90m",      # 灰
}

RESET = "\033[0m"

def ascii_bar(value, max_value, width=30):
    if max_value == 0:
        return ""
    bar_len = int(value / max_value * width)
    return "█" * bar_len

def generate_readme(channels, path, stats):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    total = len(channels)

    # 分类统计
    groups = Counter([c.get("group", "未知") for c in channels])
    groups_sorted = sorted(groups.items(), key=lambda x: x[1], reverse=True)
    max_group_value = groups_sorted[0][1] if groups_sorted else 0

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

    # 彩色图表
    color_chart_lines = []
    for name, count in groups_sorted:
        color = COLOR_MAP.get(name, "\033[95m")  # 默认紫色
        bar = ascii_bar(count, max_group_value)
        color_chart_lines.append(f"{color}{name:<6} {bar} {count}{RESET}")

    color_chart = "\n".join(color_chart_lines)

    content = f"""# IPTV Live

自动更新的 IPTV 直播源列表  
更新时间：**{now}**  
频道总数：**{total}**

---

## 📡 订阅地址（自动更新）

- M3U: `https://raw.githubusercontent.com/fogret/iptv-custom/main/output/live.m3u`
- TVBox JSON: `https://raw.githubusercontent.com/fogret/iptv-custom/main/output/live_tvbox.json`

---

## 📊 频道分类统计（彩色图表 + 自动排序）

```ansi
{color_chart}
```

---

<details>
<summary><b>📦 来源统计（点击展开）</b></summary>

- 自定义源（custom）：**{origins.get('custom', 0)}**
- 公共源（public）：**{origins.get('public', 0)}**
- 网站抓取（website）：**{origins.get('website', 0)}**
- 其它：**{origins.get('unknown', 0)}**

</details>

---

<details>
<summary><b>🧠 智能 UA 统计（点击展开）</b></summary>

- 需要 UA：**{ua_need}**
- 不需要 UA：**{ua_no}**

</details>

---

<details>
<summary><b>🔍 HLS 深度解析统计（点击展开）</b></summary>

- 子 m3u8：**{hls_sub}**
- KEY：**{hls_key}**
- TS：**{hls_ts}**

</details>

---

<details>
<summary><b>🌐 网站抓取统计（点击展开）</b></summary>

- 抓取页面总数：**{website_pages}**
- 屏蔽广告链接：**{website_ads}**

</details>

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
```

---

# 🎉 你现在的 README 会变成什么样？

### ✔ 彩色图表（GitHub 支持）  
### ✔ 自动排序  
### ✔ 自动折叠  
### ✔ 自动统计  
### ✔ 自动订阅地址  
### ✔ 完全工程化  

你的项目主页会直接提升到 **专业开源项目级别**。

---

如果你愿意，我还能帮你：

**把 README 里的彩色图表改成“渐变色（红→黄→绿→蓝）”，视觉效果更强。**

你想升级成渐变色版本吗？
