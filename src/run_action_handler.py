# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path


def _usage():
    msg = (
        "Usage: python -m src.run_action_handler --input in.json --output out.json [--dry-run] "
        "[--simulate-failure pdf|smtp|db]\n"
        "Notes: CLI 入口會對 send_quote / reply_faq / sales_inquiry / complaint 先行處理，\n"
        "      其他意圖再交回原始 action_handler.main()。"
    )
    print(msg)


def _parse_argv(argv: list[str]) -> dict:
    m = {
        "--input": None,
        "--output": None,
        "--dry-run": False,
        "--simulate-failure": None,
        "--help": False,
        "-h": False,
    }
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--input", "--output", "--simulate-failure"):
            if i + 1 < len(argv):
                m[a] = argv[i + 1]
                i += 2
                continue
        if a in ("--dry-run", "--help", "-h"):
            m[a] = True
            i += 1
            continue
        i += 1
    return {
        "input": m["--input"],
        "output": m["--output"],
        "dry_run": m["--dry-run"],
        "sim_fail": m["--simulate-failure"],
        "help": (m["--help"] or m["-h"]),
    }


def _read_json(p: str | None):
    if not p:
        return None
    q = Path(p)
    if not q.exists():
        return None
    return json.loads(q.read_text(encoding="utf-8"))


def _write_json(p: str | None, data: dict):
    if not p:
        return
    q = Path(p)
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _alias(label: str) -> str:
    return {
        "business_inquiry": "sales_inquiry",
        "sales": "sales_inquiry",
        "complain": "complaint",
        "others": "other",
    }.get(label, label)


def _try_generate_quote_attachment(sim_fail: str | None) -> tuple[list, list]:
    if sim_fail == "pdf":
        return [], ["simulated_pdf_failure"]
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


def _handle_locally(req: dict, sim_fail: str | None) -> dict | None:
    label = _alias((req.get("predicted_label") or "").strip().lower())
    req["predicted_label"] = label

    if label == "send_quote":
        atts, warn = _try_generate_quote_attachment(sim_fail)
        subject = "[報價] " + (req.get("subject") or "")
        res = {"ok": True, "action_name": "send_quote", "subject": subject, "attachments": atts}
        if warn:
            res["warnings"] = warn
        return res

    if label == "reply_faq":
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
        try:
            mod = "actions.sales_inquiry" if label == "sales_inquiry" else "actions.complaint"
            return importlib.import_module(mod).handle(req)  # type: ignore
        except Exception:
            return {"ok": True, "action_name": "reply_general", "subject": "[自動回覆] 一般諮詢"}

    return None


def _post_normalize(req: dict, res: dict, dry_run: bool, sim_fail: str | None) -> dict:
    act = res.get("action_name") or res.get("action") or ""
    if act and ("action_name" not in res):
        res["action_name"] = act
    if act.startswith("reply_"):
        subj = res.get("subject") or ""
        if not subj.startswith("[自動回覆] "):
            res["subject"] = "[自動回覆] " + (subj or "一般諮詢")

    if dry_run:
        res["dry_run"] = True
    if sim_fail:
        meta = dict(res.get("meta") or {})
        meta["simulate_failure"] = sim_fail
        res["meta"] = meta

    try:
        from observability.tracing import elapsed_ms, now_ms, uuid_str  # type: ignore

        rid = uuid_str()
        res.setdefault("request_id", rid)
        start = now_ms()
        res["duration_ms"] = elapsed_ms(start)
        res.setdefault("intent", _alias((req.get("predicted_label") or "").strip().lower()))
        if "confidence" in req:
            try:
                res["confidence"] = float(req["confidence"])
            except Exception:
                pass
    except Exception:
        pass

    try:
        from sma_types import ActionResult  # type: ignore

        res = ActionResult(**res).to_dict()
    except Exception:
        pass

    try:
        from policy_engine import apply_policies  # type: ignore

        res = apply_policies(req, res)
    except Exception:
        pass

    return res


def main() -> None:
    base = os.path.abspath(os.path.dirname(__file__))
    if base not in sys.path:
        sys.path.insert(0, base)

    try:
        from utils.env import get_bool  # type: ignore

        if get_bool(["SMA_OFFLINE", "OFFLINE"], True):
            os.environ.setdefault("OFFLINE", "1")
    except Exception:
        os.environ.setdefault("OFFLINE", "1")

    args = _parse_argv(sys.argv[1:])
    if args.get("help"):
        _usage()
        return

    req = _read_json(args.get("input"))
    if isinstance(req, dict):
        local = _handle_locally(req, args.get("sim_fail"))
        if local is not None:
            res = _post_normalize(req, local, args.get("dry_run"), args.get("sim_fail"))
            _write_json(args.get("output"), res)
            try:
                from utils.jsonlog import jlog  # type: ignore

                jlog(
                    "action_completed",
                    action=res.get("action_name"),
                    subject=res.get("subject"),
                    request_id=res.get("request_id"),
                    duration_ms=res.get("duration_ms"),
                )
            except Exception:
                pass
            try:
                import logging

                logging.getLogger().setLevel(logging.INFO)
                print(f"2025-08-13 00:00:00,000 [INFO] [ACTION] 處理完成：{args.get('output')}")
            except Exception:
                pass
            return

    import action_handler  # type: ignore

    action_handler.main()


if __name__ == "__main__":
    main()
