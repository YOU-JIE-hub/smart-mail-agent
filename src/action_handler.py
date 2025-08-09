#!/usr/bin/env python3
# 檔案位置：src/action_handler.py
# 模組用途：根據分類結果執行對應處理（工單/異動/RAG/客訴/報價）並記錄統計

import argparse
import json
import os
import subprocess
import time
from datetime import datetime

from log_writer import log_to_db  # PYTHONPATH=src 時可直接匯入
from stats_collector import increment_counter
from utils.db_tools import get_user_by_email
from utils.logger import logger
from utils.mailer import send_email_with_attachment
from utils.rag_reply import generate_rag_reply

# === [SMA] 穩定匯入：modules.* 優先，失敗則回退同層 ===
try:
    from modules.leads_logger import log_lead  # type: ignore
except Exception:
    try:
        from leads_logger import log_lead  # type: ignore
    except Exception:
        log_lead = None  # type: ignore

try:
    from modules.quotation import generate_pdf_quote  # type: ignore
except Exception:
    try:
        from quotation import generate_pdf_quote  # type: ignore
    except Exception:
        generate_pdf_quote = None  # type: ignore

try:
    from modules.quote_logger import log_quote  # type: ignore
except Exception:
    try:
        from quote_logger import log_quote  # type: ignore
    except Exception:
        log_quote = None  # type: ignore

try:
    from modules.sales_notifier import notify_sales  # type: ignore
except Exception:
    try:
        from sales_notifier import notify_sales  # type: ignore
    except Exception:
        notify_sales = None  # type: ignore


# [SMA_CHOOSE_PACKAGE_IMPORT] 穩定匯入 choose_package，提供安全預設
try:
    from modules.quotation import choose_package  # type: ignore
except Exception:
    try:
        from quotation import choose_package  # type: ignore
    except Exception:

        def choose_package(*args, **kwargs):  # type: ignore
            # 安全預設：無外部實作時回傳 'basic'
            return "basic"


def handle_tech_support(data: dict) -> str:
    logger.info("[action_handler] 處理技術支援工單")
    subprocess.run(
        [
            "python",
            "src/support_ticket.py",
            "create",
            "--subject",
            data.get("subject", ""),
            "--content",
            data.get("body", ""),
            "--summary",
            data.get("summary", ""),
            "--sender",
            data.get("sender", ""),
            "--category",
            data.get("predicted_label", ""),
            "--confidence",
            str(data.get("confidence", 0)),
        ],
        check=True,
    )
    return "已建立工單"


def handle_info_change(data: dict) -> str:
    logger.info("[action_handler] 處理資料異動申請")
    try:
        result = subprocess.run(
            [
                "python",
                "src/apply_diff.py",
                "--email",
                data.get("sender", ""),
                "--content",
                data.get("body", ""),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        try:
            output = json.loads(result.stdout or "{}")
        except Exception:
            output = {}
        status = output.get("status", "")
        pdf_path = output.get("pdf_path", "")
        if status == "updated" and pdf_path and os.path.exists(pdf_path):
            send_email_with_attachment(
                recipient=data.get("sender", ""),
                subject="RE: 資料異動確認",
                body_html="<p>您好，附件為您的異動紀錄 PDF，已完成處理。</p>",
                attachment_path=pdf_path,
            )
            return "已更新欄位 + 已寄出 PDF"
        if status == "no_change":
            return "無異動"
        return "未辨識結果"
    except Exception as e:  # pragma: no cover
        logger.error("[action_handler] 處理 info_change 失敗：%s", e)
        raise


def handle_general_inquiry(data: dict) -> str:
    logger.info("[action_handler] 啟動 RAG 回覆流程")
    query = data.get("body", "")
    kb_path = "data/knowledge/faq.md"
    answer = generate_rag_reply(query, kb_path)
    html_body = (
        "<p>您好，根據您的問題，我們提供以下說明：</p>"
        f"<p>{answer}</p><p>若仍有疑問，歡迎回信詢問。</p>"
    )
    send_email_with_attachment(
        recipient=data.get("sender", ""),
        subject=f"RE: {data.get('subject','')}",
        body_html=html_body,
    )
    return "已使用 RAG 回信"


def handle_complaint(data: dict) -> str:
    logger.info("[action_handler] 處理客訴信件")
    recipient = data.get("sender") or data.get("email") or ""
    subject = data.get("subject", "")
    user = get_user_by_email("data/users.db", recipient) if recipient else None
    name = user.get("name") if user else "貴賓"
    html = f"""<p>{name}您好：</p>
    <p>我們已收到您的寶貴意見，對於此次造成的不便，我們深感抱歉。</p>
    <p>我們將轉交專人儘速處理，並努力避免類似情況再次發生。</p>
    <p>若有任何補充需求，歡迎直接回覆此信。</p>
    <p>客服團隊 敬上<br>{datetime.now().strftime('%Y-%m-%d')}</p>"""
    send_email_with_attachment(
        recipient=recipient,
        subject=f"RE: {subject} - 很抱歉造成您的困擾",
        body_html=html,
    )
    return "已寄送道歉信"


def handle_quotation(data: dict) -> str:
    logger.info("[action_handler] 處理報價需求")
    subject = data.get("subject", "")
    content = data.get("body", "")
    recipient = data.get("sender", "")
    sel = choose_package(subject, content)
    if sel.get("needs_manual"):
        send_email_with_attachment(
            recipient=recipient,
            subject=f"RE: {subject} - 已收到需求",
            body_html="<p>您好，已收到您的需求，專人將盡速與您聯繫。</p>",
        )
        return "待人工處理"
    pdf_path = generate_pdf_quote(sel["package"], recipient)
    send_email_with_attachment(
        recipient=recipient,
        subject=f"RE: {subject} - 報價單",
        body_html=(f"<p>您好，附件為 <b>{sel['package']}</b> 報價單，若有疑問歡迎回覆。</p>"),
        attachment_path=pdf_path,
    )
    log_quote(recipient, sel["package"], pdf_path, sent_status="success")
    log_lead(recipient, sel["package"], pdf_path)
    return f"已寄送 {sel['package']} 報價單"


def handle_unknown(data: dict) -> str:
    logger.info("[action_handler] 未定義行為：%s", data.get("predicted_label"))
    return "未定義行為，已紀錄"


def route_action(label: str, data: dict) -> None:
    subject = data.get("subject", "")
    body = data.get("body", "")
    summary = data.get("summary", "")
    confidence = float(data.get("confidence", 0))
    error = ""
    action_result = "none"
    start = time.time()
    try:
        handlers = {
            "請求技術支援": handle_tech_support,
            "申請修改資訊": handle_info_change,
            "詢問流程或規則": handle_general_inquiry,
            "投訴與抱怨": handle_complaint,
            "業務接洽或報價": handle_quotation,
        }
        handler = handlers.get(label, handle_unknown)
        action_result = handler(data)
    except Exception as e:
        error = str(e)
        logger.error("[action_handler] 執行 '%s' 失敗：%s", label, error)

    # 寫 log（不中斷）
    try:
        log_to_db(
            subject=subject,
            content=body,
            summary=summary,
            label=label,
            confidence=confidence,
            action=action_result,
            error=error,
        )
    except Exception as e:  # pragma: no cover
        logger.warning("[action_handler] log 寫入失敗：%s", e)

    elapsed = round(time.time() - start, 3)
    increment_counter(label, elapsed)
    logger.info("[action_handler] 統計完成：%s (+1)，耗時 %.3fs", label, elapsed)


def main():
    ap = argparse.ArgumentParser(description="根據分類結果觸發對應處理")
    ap.add_argument("--json", required=True, help="分類結果 JSON 檔案路徑")
    args = ap.parse_args()
    with open(args.json, encoding="utf-8") as f:
        data = json.load(f)
    label = data.get("predicted_label", "其他")
    logger.info("[action_handler] 執行分類：%s → %s", args.json, label)
    route_action(label, data)


if __name__ == "__main__":
    main()
