#!/usr/bin/env python3
# 檔案位置：src/utils/logger.py
# 模組用途：統一建立 Smart-Mail-Agent 專案的主 logger
# 支援輸出至 logs/run.log 檔案與 Console，並降低第三方套件噪音

import logging
import warnings
from pathlib import Path

# === 建立 logs 資料夾 ===
Path("logs").mkdir(exist_ok=True)

# === 設定 log 檔案位置與格式 ===
LOG_FILE = "logs/run.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# === 建立 logger 實例 ===
logger = logging.getLogger("smart-mail-agent")
logger.setLevel(logging.INFO)

# 避免重複添加 handler（多次 import 時）
if not logger.handlers:
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    # 檔案輸出 handler
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Console 輸出 handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # 加入 handler
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# === 壓低外部套件 log 噪音 ===
for module in ["urllib3", "httpx", "openai", "requests", "langchain"]:
    logging.getLogger(module).setLevel(logging.WARNING)

# 特別壓低 FAISS log
logging.getLogger("faiss.loader").setLevel(logging.ERROR)

# === 忽略某些警告 ===
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="langchain")
