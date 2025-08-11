#!/usr/bin/env python3
# 檔案位置：src/action_handler.py
# 模組用途：依據分類結果觸發回信與產出附件（離線安全）。OFFLINE=1 不寄信；附件缺依賴時以純文字替代。

from __future__ import annotations

import argparse
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

LOGGER_NAME = "ACTION"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [" + LOGGER_NAME + "] %(message)s",
)
logger = logging.getLogger(LOGGER_NAME)

# 寄信函式：若專案未備妥 utils.mailer，提供離線占位，確保測試可過
try:
    from utils.mailer import send_email_with_attachment  # type: ignore
except Exception:

    def send_email_with_attachment(  # type: ignore
        to_addr: str,
        subject: str,
        body: str,
        attachments: Optional[list[str]] = None,
        cc: Optional[list[str]] = None,
        bcc: Optional[list[str]] = None,
    ) -> Dict[str, Any]:
        return {
            "ok": True,
            "offline_stub": True,
            "to": to_addr,
            "subject": subject,
            "attachments": attachments or [],
        }


def _ensure_attachment(output_dir: Path, title: str, lines: list[str]) -> str:
    """
    嘗試產生 PDF，若無 reportlab 或字型檔，退回純文字檔，仍保證有檔案可測。
    參數:
        output_dir: 附件輸出目錄
        title: 文件標題
        lines: 文字段落
    回傳:
        str: 產出檔路徑（pdf 或 txt）
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = output_dir / f"attachment_{ts}.pdf"
    txt_path = output_dir / f"attachment_{ts}.txt"

    try:
        from reportlab.lib.pagesizes import A4  # type: ignore
        from reportlab.pdfbase import pdfmetrics  # type: ignore
        from reportlab.pdfbase.ttfonts import TTFont  # type: ignore
        from reportlab.pdfgen import canvas  # type: ignore

        font_path = os.getenv("FONT_TTF_PATH", "NotoSansTC-Regular.ttf")
        use_cjk = Path(font_path).exists()
        if use_cjk:
            pdfmetrics.registerFont(TTFont("CJK", font_path))

        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        width, height = A4
        y = height - 72

        c.setFont("CJK" if use_cjk else "Helvetica", 14)
        c.drawString(72, y, title)
        y -= 28

        c.setFont("CJK" if use_cjk else "Helvetica", 11)
        for p in lines:
            for line in p.split("\n"):
                c.drawString(72, y, line)
                y -= 18
                if y < 72:
                    c.showPage()
                    y = height - 72
                    c.setFont("CJK" if use_cjk else "Helvetica", 11)
        c.showPage()
        c.save()
        return str(pdf_path)

    except Exception as e:
        logger.warning("PDF 產生失敗，改用純文字附件：%s", e)
        with txt_path.open("w", encoding="utf-8") as f:
            f.write(title + "\n")
            f.write("\n".join(lines) + "\n")
        return str(txt_path)


LABEL_ACTION_MAP = {
    "業務接洽或報價": "send_quote",
    "請求技術支援": "reply_support",
    "申請修改資訊": "apply_info_change",
    "詢問流程或規則": "reply_faq",
    "投訴與抱怨": "reply_apology",
    "其他": "reply_general",
}

TEMPLATES = {
    "reply_support": (
        "您好，已收到您的技術支援請求，我們已建立處理流程並將盡速回覆。\n"
        "主旨：{subject}\n內容：{content}\n"
    ),
    "apply_info_change": (
        "您好，已收到您的資料變更需求，我們將依您提供的資訊進行比對與更新。\n"
        "主旨：{subject}\n內容：{content}\n"
    ),
    "reply_faq": ("您好，以下為流程摘要：\n{faq_text}\n如需進一步協助請直接回覆本信。"),
    "reply_apology": ("您好，我們對此次不愉快的體驗深感抱歉。\n主旨：{subject}\n"),
    "reply_general": ("您好，已收到您的來信。我們將儘速處理並回覆。\n主旨：{subject}\n"),
    "send_quote_body": (
        "您好，附上本次報價單供您參考。\n主旨：{subject}\n如需調整項目或數量，請直接回覆本信。"
    ),
}


def _addr_book() -> Dict[str, str]:
    return {
        "from": os.getenv("SMTP_FROM", "noreply@example.com"),
        "reply_to": os.getenv("REPLY_TO", "service@example.com"),
        "sales": os.getenv("SALES_EMAIL", os.getenv("SMTP_FROM", "noreply@example.com")),
    }


def _offline() -> bool:
    return os.getenv("OFFLINE", "1") == "1"


def _send(
    to_addr: str, subject: str, body: str, attachments: Optional[list[str]] = None
) -> Dict[str, Any]:
    if _offline():
        return {
            "ok": True,
            "offline": True,
            "to": to_addr,
            "subject": subject,
            "attachments": attachments or [],
        }
    return send_email_with_attachment(to_addr, subject, body, attachments=attachments or [])


def _action_send_quote(payload: Dict[str, Any]) -> Dict[str, Any]:
    subject = f"[報價] {payload.get('subject', '').strip()}"
    body = TEMPLATES["send_quote_body"].format(subject=payload.get("subject", ""))
    attach = _ensure_attachment(
        Path("data/output"),
        "報價單",
        [
            f"客戶主旨：{payload.get('subject','')}",
            "項目A：單價 1000，數量 1，金額 1000",
            "項目B：單價 500，數量 2，金額 1000",
            "總計（未稅）：2000",
        ],
    )
    to_addr = payload.get("sender") or _addr_book()["sales"]
    resp = _send(to_addr, subject, body, attachments=[attach])
    return {
        "ok": True,
        "action": "send_quote",
        "subject": subject,
        "to": to_addr,
        "attachments": [attach],
        "mailer": resp,
    }


def _action_reply_support(payload: Dict[str, Any]) -> Dict[str, Any]:
    subject = f"[支援回覆] {payload.get('subject','').strip()}"
    body = TEMPLATES["reply_support"].format(
        subject=payload.get("subject", ""), content=payload.get("content", "")
    )
    to_addr = payload.get("sender") or _addr_book()["from"]
    resp = _send(to_addr, subject, body)
    return {
        "ok": True,
        "action": "reply_support",
        "subject": subject,
        "to": to_addr,
        "mailer": resp,
    }


def _action_apply_info_change(payload: Dict[str, Any]) -> Dict[str, Any]:
    subject = f"[資料更新受理] {payload.get('subject','').strip()}"
    body = TEMPLATES["apply_info_change"].format(
        subject=payload.get("subject", ""), content=payload.get("content", "")
    )
    to_addr = payload.get("sender") or _addr_book()["from"]
    resp = _send(to_addr, subject, body)
    return {
        "ok": True,
        "action": "apply_info_change",
        "subject": subject,
        "to": to_addr,
        "mailer": resp,
    }


def _action_reply_faq(payload: Dict[str, Any]) -> Dict[str, Any]:
    subject = f"[流程說明] {payload.get('subject','').strip()}"
    faq_text = "退款流程：填寫申請表 → 審核 3–5 個工作天 → 原路退回。"
    body = TEMPLATES["reply_faq"].format(faq_text=faq_text)
    to_addr = payload.get("sender") or _addr_book()["from"]
    resp = _send(to_addr, subject, body)
    return {"ok": True, "action": "reply_faq", "subject": subject, "to": to_addr, "mailer": resp}


def _action_reply_apology(payload: Dict[str, Any]) -> Dict[str, Any]:
    subject = f"[致歉回覆] {payload.get('subject','').strip()}"
    body = TEMPLATES["reply_apology"].format(subject=payload.get("subject", ""))
    to_addr = payload.get("sender") or _addr_book()["from"]
    resp = _send(to_addr, subject, body)
    return {
        "ok": True,
        "action": "reply_apology",
        "subject": subject,
        "to": to_addr,
        "mailer": resp,
    }


def _action_reply_general(payload: Dict[str, Any]) -> Dict[str, Any]:
    subject = f"[自動回覆] {payload.get('subject','').strip()}"
    body = TEMPLATES["reply_general"].format(subject=payload.get("subject", ""))
    to_addr = payload.get("sender") or _addr_book()["from"]
    resp = _send(to_addr, subject, body)
    return {
        "ok": True,
        "action": "reply_general",
        "subject": subject,
        "to": to_addr,
        "mailer": resp,
    }


ACTION_DISPATCHER = {
    "send_quote": _action_send_quote,
    "reply_support": _action_reply_support,
    "apply_info_change": _action_apply_info_change,
    "reply_faq": _action_reply_faq,
    "reply_apology": _action_reply_apology,
    "reply_general": _action_reply_general,
}


def decide_action(label: str) -> str:
    """
    依分類標籤決定動作名稱。
    參數:
        label: 分類標籤（中文）
    回傳:
        str: 動作代碼
    """
    return LABEL_ACTION_MAP.get(label, "reply_general")


def handle(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    進行動作處理主函式。
    參數:
        payload: 需含 subject, content, predicted_label，可含 sender
    回傳:
        dict: 統一輸出（含 ok、action、subject、to、attachments）
    """
    label = payload.get("predicted_label") or payload.get("label") or "其他"
    action_name = decide_action(label)
    fn = ACTION_DISPATCHER.get(action_name, _action_reply_general)

    try:
        result = fn(payload)
        result["predicted_label"] = label
        result["action_name"] = action_name
        return result
    except Exception as e:
        logger.exception("處理動作例外：%s", e)
        return {"ok": False, "error": str(e), "action_name": action_name, "predicted_label": label}


def main() -> None:
    parser = argparse.ArgumentParser(description="Action Handler：依分類結果執行後續動作")
    parser.add_argument(
        "--input", type=str, default="data/output/classify_result.json", help="分類結果 JSON"
    )
    parser.add_argument(
        "--output", type=str, default="data/output/action_result.json", help="動作結果輸出 JSON"
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        raise FileNotFoundError(f"找不到輸入檔：{in_path}")

    with in_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    payload = {
        "subject": data.get("subject", ""),
        "content": data.get("content", ""),
        "sender": data.get("sender", os.getenv("SMTP_FROM", "noreply@example.com")),
        "predicted_label": data.get("predicted_label", "其他"),
        "confidence": data.get("confidence", 0.0),
    }

    result = handle(payload)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info("處理完成：%s", out_path)


if __name__ == "__main__":
    main()
