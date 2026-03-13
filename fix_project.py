import os
import re

ROOT = "src"

EDGE_PATTERN = re.compile(r"# User's Edge browser tabs metadata[\s\S]*", re.MULTILINE)

def clean_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # 删除 Edge 注入垃圾内容
    content = re.sub(EDGE_PATTERN, "", content)

    # 修复 import 路径
    content = re.sub(r"from\s+(collectors|processors|validators|exporters|epg|utils)\s+import",
                     r"from src.\1 import", content)
    content = re.sub(r"from\s+(\w+)\.", r"from src.\1.", content)

    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✔ 修复: {path}")

def scan():
    for root, dirs, files in os.walk(ROOT):
        for file in files:
            if file.endswith(".py"):
                clean_file(os.path.join(root, file))

if __name__ == "__main__":
    scan()
    print("\n🎉 全部 Python 文件修复完成！")
