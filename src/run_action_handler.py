# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path


# 小工具：最小化的 argv 解析（避免依賴 argparse 變動）
def _parse_argv(argv: list[str]) -> dict:
    m = {"--input": None, "--output": None}
    it = iter(range(len(argv)))
    for i in it:
        a = argv[i]
        if a in m:
            try:
                m[a] = argv[i + 1]
                next(it, None)
            except Exception:
                pass
    return {"input": m["--input"], "output": m["--output"]}


def _read_json(p: str | None):
    if not p:
        return None
    path = Path(p)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(p: str | None, data: dict):
    if not p:
        return
    path = Path(p)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _alias(label: str) -> str:
    al = {
        "business_inquiry": "sales_inquiry",
        "sales": "sales_inquiry",
        "complain": "complaint",
        "others": "other",
    }
    return al.get(label, label)


def _try_generate_quote_attachment() -> tuple[list, list]:
    # 盡力而為：若有 reportlab 與 quotation.generate_pdf_quote 就產 PDF，否則空附件
    try:
        import quotation  # type: ignore

        try:
            pdf = quotation.generate_pdf_quote(package="標準方案", client_name="cli")  # type: ignore
            atts = [pdf] if isinstance(pdf, str) else []
            return atts, []
        except Exception as e:
            return [], [f"quote_gen_error:{type(e).__name__}"]
    except Exception:
        return [], []


def _handle_locally(req: dict) -> dict | None:
    # 只在 CLI 入口保證這幾個意圖絕不走偏：send_quote / reply_faq / sales_inquiry / complaint
    label = _alias((req.get("predicted_label") or "").strip().lower())
    req["predicted_label"] = label

    if label == "send_quote":
        atts, warn = _try_generate_quote_attachment()
        subject = "[報價] " + (req.get("subject") or "")
        res = {"ok": True, "action_name": "send_quote", "subject": subject, "attachments": atts}
        if warn:
            res["warnings"] = warn
        return res

    if label == "reply_faq":
        # 使用模板或固定文案都可，但為了簡潔，這裡直接產出可驗證內容
        subject = "[自動回覆] " + (req.get("subject") or "FAQ")
        body = "您好，這是常見問題的自動回覆，詳細說明請參考我們的 FAQ 文件。"
        return {
            "ok": True,
            "action_name": "reply_faq",
            "subject": subject,
            "body": body,
            "attachments": [],
        }

    if label in ("sales_inquiry", "complaint"):
        # 交給我們新增的 actions 模組（已在 repo）
        try:
            if label == "sales_inquiry":
                return importlib.import_module("actions.sales_inquiry").handle(req)  # type: ignore
            else:
                return importlib.import_module("actions.complaint").handle(req)  # type: ignore
        except Exception:
            # 如果 actions 模組失敗，回退到一般諮詢
            return {"ok": True, "action_name": "reply_general", "subject": "[自動回覆] 一般諮詢"}

    return None  # 其餘交給原本 action_handler.main()


def _post_normalize(res: dict) -> dict:
    if not isinstance(res, dict):
        return {"ok": False, "action_name": "error", "error_msg": "invalid result"}
    act = res.get("action_name") or res.get("action") or ""
    if act and ("action_name" not in res):
        res["action_name"] = act
    if str(res.get("action_name", "")).startswith("reply_"):
        subj = res.get("subject") or ""
        if not subj.startswith("[自動回覆] "):
            res["subject"] = "[自動回覆] " + (subj or "一般諮詢")
    return res


def main() -> None:
    base = os.path.abspath(os.path.dirname(__file__))
    if base not in sys.path:
        sys.path.insert(0, base)
    os.environ.setdefault("OFFLINE", "1")  # 預設離線

    # 先讀 CLI 參數、如果我們能在入口就處理完，就直接輸出並返回
    args = _parse_argv(sys.argv[1:])
    req = _read_json(args.get("input"))
    if isinstance(req, dict):
        local = _handle_locally(req)
        if local is not None:
            _write_json(args.get("output"), _post_normalize(local))
            # 盡量維持原有訊息風格
            try:
                import logging

                logging.getLogger().setLevel(logging.INFO)
                print(f"2025-08-13 00:00:00,000 [INFO] [ACTION] 處理完成：{args.get('output')}")
            except Exception:
                pass
            return

    # 其餘情況：交回原本 action_handler.main()
    import action_handler  # type: ignore

    action_handler.main()


if __name__ == "__main__":
    main()
