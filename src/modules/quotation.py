#!/usr/bin/env python3
# 檔案位置：src/modules/quotation.py
# 模組用途：分析信件內容決定報價方案 → 產出報價 PDF → 紀錄 DB → 寄送副本給業務窗口

import os
import warnings
from datetime import datetime

from fpdf import FPDF

from modules.quote_logger import log_quote
from modules.sales_notifier import notify_sales
from utils.logger import logger

# 報價方案對照表
PACKAGE_MAP = {
    "基礎": {"price": "NT$980 / 月", "desc": "適合個人與小型團隊，含基本自動化功能"},
    "專業": {"price": "NT$2,980 / 月", "desc": "支援批次處理、自動分類、排程功能"},
    "企業": {"price": "客製報價", "desc": "支援 API 整合、帳號管理、SLA、自訂流程"},
}

# 預設字型路徑（可由 .env 覆寫）
DEFAULT_FONT_PATH = os.getenv("QUOTE_FONT_PATH", "assets/fonts/NotoSansTC-Regular.ttf")


def choose_package(subject: str, content: str) -> dict:
    """
    根據信件內容推論報價方案（rule-based）

    參數:
        subject (str): 郵件主旨
        content (str): 郵件內容

    回傳:
        dict: {'package': 報價類型, 'needs_manual': 是否需人工處理}
    """
    text = (subject + content).lower()
    logger.info("分析報價需求內容：%s...", text[:40])

    if any(k in text for k in ["api", "客製", "整合", "企業", "大量"]):
        return {"package": "企業", "needs_manual": True}
    elif any(k in text for k in ["分類", "排程", "自動化"]):
        return {"package": "專業", "needs_manual": False}
    elif any(k in text for k in ["價格", "試用", "多少錢", "報價"]):
        return {"package": "基礎", "needs_manual": False}
    else:
        return {"package": "企業", "needs_manual": True}


def generate_pdf_quote(package: str, client_name: str) -> str:
    """
    產生報價單 PDF 並寄送副本給業務，含 DB 紀錄與例外處理

    參數:
        package (str): 報價方案（基礎 / 專業 / 企業）
        client_name (str): 客戶 email 或名稱

    回傳:
        str: PDF 完整儲存路徑
    """
    warnings.filterwarnings("ignore", category=UserWarning, module="fpdf.ttfonts")

    if package not in PACKAGE_MAP:
        raise ValueError(f"[報價錯誤] 未知報價方案：{package}")

    data = PACKAGE_MAP[package]
    today_str = datetime.now().strftime("%Y%m%d")
    timestamp = datetime.now().strftime("%H%M%S")
    safe_name = client_name.replace(" ", "").replace("@", "_").replace(".", "_")[:20]
    filename = f"quote_{package}_{safe_name}_{timestamp}.pdf"
    archive_dir = os.path.join("data", "archive", "quotes", today_str)
    os.makedirs(archive_dir, exist_ok=True)
    full_path = os.path.join(archive_dir, filename)

    # PDF 建立
    if not os.path.exists(DEFAULT_FONT_PATH):
        raise FileNotFoundError(f"[報價錯誤] 找不到中文字型：{DEFAULT_FONT_PATH}")

    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.add_font("Noto", "", DEFAULT_FONT_PATH, uni=True)
        pdf.set_font("Noto", size=14)
        pdf.cell(200, 10, txt="Smart-Mail-Agent 報價單", ln=True, align="C")

        pdf.set_font("Noto", size=12)
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"客戶名稱：{client_name}", ln=True)
        pdf.cell(200, 10, txt=f"方案類型：{package}", ln=True)
        pdf.cell(200, 10, txt=f"價格資訊：{data['price']}", ln=True)
        pdf.multi_cell(0, 10, txt=f"方案說明：{data['desc']}")

        pdf.output(full_path)
        logger.info("[報價產出] PDF 完成：%s", full_path)
    except Exception as e:
        logger.error("[報價失敗] PDF 產出錯誤：%s", str(e))
        raise

    # 紀錄至報價記錄資料庫
    try:
        log_quote(client_name=client_name, package=package, pdf_path=full_path)
    except Exception as e:
        logger.warning("[報價紀錄失敗] 寫入 quote_log.db 錯誤：%s", str(e))

    # 寄送副本給業務
    try:
        result = notify_sales(client_name=client_name, package=package, pdf_path=full_path)
        if result:
            logger.info("[業務通知] 已通知業務窗口")
        else:
            logger.warning("[業務通知失敗] 無法寄送副本")
    except Exception as e:
        logger.warning("[業務通知例外] 發送過程錯誤：%s", str(e))

    return full_path
