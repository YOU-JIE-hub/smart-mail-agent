from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

from ai_rpa.actions import write_json
from smart_mail_agent.utils.logger import get_logger

# 可選模組（存在就用）
try:
    from ai_rpa import ocr  # type: ignore
except Exception:  # pragma: no cover
    ocr = None
try:
    from ai_rpa import scraper  # type: ignore
except Exception:  # pragma: no cover
    scraper = None
try:
    from ai_rpa import nlp  # type: ignore
except Exception:  # pragma: no cover
    nlp = None
from ai_rpa import nlp_llm

logger = get_logger("ai_rpa.main")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="ai-rpa", description="AI+RPA Pipeline")
    p.add_argument("--input-path", dest="input_path", type=str, default="", help="輸入路徑或文字檔 / 網址")
    p.add_argument(
        "--output", dest="output", type=str, default="data/output/report.json", help="輸出檔（完整檔名或目錄）"
    )
    p.add_argument("--tasks", type=str, default="ocr,scrape,nlp,actions", help="任務清單，以逗號分隔")
    p.add_argument("--dry-run", action="store_true", help="僅顯示不寫檔")
    return p.parse_args()


def _normalize_output_path(out: str) -> Path:
    outp = Path(out)
    return outp / "report.json" if (outp.is_dir() or not outp.suffix) else outp


def _to_text(x) -> str:
    if x is None:
        return ""
    if isinstance(x, (list, tuple)):
        return "\n".join(_to_text(y) for y in x)
    if isinstance(x, dict):
        for k in ("text", "content", "ocr_text", "body", "data"):
            if k in x and x[k]:
                return _to_text(x[k])
        # 兜底：把所有簡單值拼成可讀文本
        try:
            items = []
            for k, v in x.items():
                if isinstance(v, (str, int, float)):
                    items.append(f"{k}: {v}")
            return "\n".join(items)
        except Exception:
            return ""
    return str(x)


def run_pipeline(args: argparse.Namespace) -> Dict[str, Any]:
    tasks: List[str] = [t.strip() for t in (args.tasks or "").split(",") if t.strip()]
    result: Dict[str, Any] = {"ok": True, "tasks": tasks, "artifacts": {}}
    text_corpus = ""

    # 1) OCR
    if "ocr" in tasks and ocr and args.input_path:
        ip = args.input_path
        try:
            ocr_out = ocr.run_ocr(ip)  # 允許回傳 dict/list/str
            piece = _to_text(ocr_out)
            text_corpus += (piece + "\n") if piece else ""
            result["artifacts"]["ocr"] = {"input": ip, "chars": len(piece)}
        except Exception as e:
            logger.exception("OCR 失敗：%s", e)
            result.setdefault("errors", []).append({"stage": "ocr", "error": str(e)})

    # 2) Scrape
    if "scrape" in tasks and scraper and args.input_path.startswith("http"):
        try:
            sc = scraper.scrape_to_text(args.input_path)
            piece = _to_text(sc)
            text_corpus += (piece + "\n") if piece else ""
            result["artifacts"]["scrape"] = {"url": args.input_path}
        except Exception as e:
            logger.exception("Scraper 失敗：%s", e)
            result.setdefault("errors", []).append({"stage": "scrape", "error": str(e)})

    # 3) NLP（若存在）
    if "nlp" in tasks and nlp:
        try:
            analysis = nlp.analyze_text(text_corpus)
            result["artifacts"]["nlp"] = analysis
        except Exception as e:
            logger.exception("NLP 失敗：%s", e)
            result.setdefault("errors", []).append({"stage": "nlp", "error": str(e)})

    # 4) LLM 摘要（退化可用）
    try:
        llm_out = nlp_llm.summarize(text_corpus)
        result["artifacts"]["llm"] = llm_out
    except Exception as e:
        logger.exception("LLM 摘要失敗：%s", e)
        result.setdefault("errors", []).append({"stage": "llm", "error": str(e)})

    # 5) Actions（輸出 JSON）
    if "actions" in tasks:
        out_file = _normalize_output_path(args.output)
        if not args.dry_run:
            write_json(result, out_file)
        else:
            logger.info("[dry-run] 將輸出到：%s", out_file)

    return result


def main() -> None:
    args = _parse_args()
    run_pipeline(args)


if __name__ == "__main__":
    main()
