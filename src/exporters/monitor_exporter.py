import json
import os

def export_monitor_ui():
    os.makedirs("output", exist_ok=True)

    with open("output/monitor.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    html = """
    <html>
    <head>
        <meta charset="utf-8">
        <title>IPTV 频道监控</title>
        <style>
            body { font-family: Arial; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ccc; padding: 8px; }
            th { background: #eee; }
            .bad { background: #ffdddd; }
            .warn { background: #fff0cc; }
            .good { background: #ddffdd; }
        </style>
    </head>
    <body>
        <h2>IPTV 频道监控</h2>
        <table>
            <tr>
                <th>频道</th>
                <th>分组</th>
                <th>评分</th>
                <th>延迟(ms)</th>
                <th>可用性</th>
                <th>URL</th>
            </tr>
    """

    for ch in data:
        score = ch["score"]
        cls = "good" if score >= 80 else "warn" if score >= 60 else "bad"

        html += f"""
        <tr class="{cls}">
            <td>{ch['name']}</td>
            <td>{ch['group']}</td>
            <td>{ch['score']}</td>
            <td>{ch['latency']}</td>
            <td>{"✔" if ch['alive'] else "✘"}</td>
            <td>{ch['url']}</td>
        </tr>
        """

    html += """
        </table>
    </body>
    </html>
    """

    with open("output/monitor.html", "w", encoding="utf-8") as f:
        f.write(html)
