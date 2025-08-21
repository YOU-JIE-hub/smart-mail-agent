from __future__ import annotations

#!/usr/bin/env python3
# 檔案位置：src/action_handler.py
import argparse
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

LOGGER_NAME = "ACTION"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [" + LOGGER_NAME + "] %(message)s",
)
logger = logging.getLogger(LOGGER_NAME)

# 嘗試載入 mailer；存在新版/舊版簽名差異，_send() 會相容呼叫
try:
    from utils.mailer import send_email_with_attachment  # type: ignore
except Exception:
    # 完全沒有 mailer 模組時的離線占位

    def send_email_with_attachment(*args, **kwargs) -> bool:  # type: ignore
        return True


def _ensure_attachment(output_dir: Path, title: str, lines: list[str]) -> str:
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
        w, h = A4
        y = h - 72
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
                    y = h - 72
                    c.setFont("CJK" if use_cjk else "Helvetica", 11)
        c.showPage()
        c.save()
        return str(pdf_path)
    except Exception as e:
        logger.warning("PDF 產生失敗，改用純文字附件：%s", e)
        txt_path.write_text(title + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
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
    "reply_support": "您好，已收到您的技術支援請求。\n主旨：{subject}\n內容：{content}\n",
    "apply_info_change": "您好，已受理您的資料變更需求。\n主旨：{subject}\n內容：{content}\n",
    "reply_faq": "您好，以下為流程摘要：\n{faq_text}\n如需進一步協助請直接回覆本信。",
    "reply_apology": "您好，我們對此次不愉快的體驗深感抱歉。\n主旨：{subject}\n",
    "reply_general": "您好，已收到您的來信。我們將儘速處理並回覆。\n主旨：{subject}\n",
    "send_quote_body": "您好，附上本次報價單供您參考。\n主旨：{subject}\n",
}


def _addr_book() -> dict[str, str]:
    return {
        "from": os.getenv("SMTP_FROM", "noreply@example.com"),
        "reply_to": os.getenv("REPLY_TO", "service@example.com"),
        "sales": os.getenv("SALES_EMAIL", os.getenv("SMTP_FROM", "noreply@example.com")),
    }


def _offline() -> bool:
    return os.getenv("OFFLINE", "1") == "1"


def _send(to_addr: str, subject: str, body: str, attachments: list[str] | None = None) -> Any:
    """相容新版與舊版 mailer 簽名；OFFLINE 直接回成功。"""
    if _offline():
        return {
            "ok": True,
            "offline": True,
            "to": to_addr,
            "subject": subject,
            "attachments": attachments or [],
        }
    # 優先嘗試新版（recipient/body_html/attachment_path）
    try:
        first_path = (attachments or [None])[0]
        return send_email_with_attachment(
            recipient=to_addr, subject=subject, body_html=body, attachment_path=first_path
        )  # type: ignore
    except TypeError:
        # 回退到舊版（to_addr/body/attachments）
        return send_email_with_attachment(to_addr, subject, body, attachments=attachments or [])  # type: ignore


def _action_send_quote(payload: dict[str, Any]) -> dict[str, Any]:
    subject = f"[報價] {payload.get('subject', '').strip()}"
    body = TEMPLATES["send_quote_body"].format(subject=payload.get("subject", ""))
    attach = _ensure_attachment(
        Path("data/output"),
        "報價單",
        [
            f"客戶主旨：{payload.get('subject', '')}",
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


def _action_reply_support(payload: dict[str, Any]) -> dict[str, Any]:
    subject = f"[支援回覆] {payload.get('subject', '').strip()}"
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


def _action_apply_info_change(payload: dict[str, Any]) -> dict[str, Any]:
    subject = f"[資料更新受理] {payload.get('subject', '').strip()}"
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


def _action_reply_faq(payload: dict[str, Any]) -> dict[str, Any]:
    subject = f"[流程說明] {payload.get('subject', '').strip()}"
    body = TEMPLATES["reply_faq"].format(
        faq_text="退款流程：填寫申請表 → 審核 3–5 個工作天 → 原路退回。"
    )
    to_addr = payload.get("sender") or _addr_book()["from"]
    resp = _send(to_addr, subject, body)
    return {
        "ok": True,
        "action": "reply_faq",
        "subject": subject,
        "to": to_addr,
        "mailer": resp,
    }


def _action_reply_apology(payload: dict[str, Any]) -> dict[str, Any]:
    subject = f"[致歉回覆] {payload.get('subject', '').strip()}"
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


def _action_reply_general(payload: dict[str, Any]) -> dict[str, Any]:
    subject = f"[自動回覆] {payload.get('subject', '').strip()}"
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
    return LABEL_ACTION_MAP.get(label, "reply_general")


def handle(payload: dict[str, Any]) -> dict[str, Any]:
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
        return {
            "ok": False,
            "error": str(e),
            "action_name": action_name,
            "predicted_label": label,
        }


# 介面別名：讓 email_processor 可 from action_handler import route_action
def route_action(label: str, payload: dict[str, Any]) -> dict[str, Any]:
    payload = dict(payload or {})
    payload.setdefault("predicted_label", label)
    return handle(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Action Handler：依分類結果執行後續動作")
    parser.add_argument("--input", type=str, default="data/output/classify_result.json")
    parser.add_argument("--output", type=str, default="data/output/action_result.json")
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        raise FileNotFoundError(f"找不到輸入檔：{in_path}")
    data = json.loads(in_path.read_text(encoding="utf-8"))

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
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("處理完成：%s", out_path)


if __name__ == "__main__":
    main()
