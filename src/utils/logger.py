import logging
import os

# 创建日志目录
os.makedirs("logs", exist_ok=True)

# 配置 logger
logger = logging.getLogger("iptv")
logger.setLevel(logging.INFO)

# 输出到控制台
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 输出到文件
file_handler = logging.FileHandler("logs/run.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)

# 日志格式
formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# 添加 handler
logger.addHandler(console_handler)
logger.addHandler(file_handler)
