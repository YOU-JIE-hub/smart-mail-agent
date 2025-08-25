from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List

from ai_rpa import file_classifier, nlp, ocr, scraper
from ai_rpa.actions import write_json


def _parse_args():
    p = argparse.ArgumentParser(prog="ai-rpa", description="AI+RPA Pipeline")
    p.add_argument("--input-path", dest="input_path", default=None)
    p.add_argument("--output", dest="output", default=None)
    p.add_argument(
        "--tasks",
        dest="tasks",
        default=None,
        help="Comma list: ocr,scrape,classify_files,nlp,actions",
    )
    p.add_argument("--url", dest="url", default=None)
    p.add_argument(
        "--config", dest="config", default=None, help="YAML config: tasks/input_path/output/url"
    )
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()


def _norm_text(x) -> str:
    if isinstance(x, str):
        return x
    if isinstance(x, dict):
        return x.get("text") or x.get("content") or ""
    if isinstance(x, (list, tuple)):
        return "\n".join(str(i) for i in x)
    return "" if x is None else str(x)


def run_pipeline(args) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    texts: List[str] = []

    tasks = [t.strip() for t in (args.tasks or "").split(",") if t.strip()]
    ip = args.input_path

    if "ocr" in tasks and ip:
        try:
            r = ocr.run_ocr(Path(ip))
        except Exception as e:
            r = {"error": str(e)}
        results["ocr"] = r
        texts.append(_norm_text(r))

    if "scrape" in tasks:
        try:
            r = scraper.scrape(args.url) if args.url else []
        except Exception as e:
            r = {"error": str(e)}
        results["scrape"] = r
        if isinstance(r, list):
            texts.extend([_norm_text(d) for d in r])

    if "classify_files" in tasks and ip:
        try:
            r = file_classifier.classify_dir(Path(ip))
        except Exception as e:
            r = {"error": str(e)}
        results["classify_files"] = r

    if "nlp" in tasks:
        try:
            n = nlp.analyze_text("\n".join([t for t in texts if t]))
        except Exception as e:
            n = {"error": str(e)}
        results["nlp"] = n

    if "actions" in tasks and not args.dry_run:
        out = args.output or "data/output/report.json"
        write_json(results, out)

    return results


def main() -> int:
    args = _parse_args()

    # YAML config（若提供）：僅補上 CLI 未提供的欄位
    if args.config:
        import yaml

        cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8")) or {}
        if not args.tasks:
            ts = cfg.get("tasks", [])
            args.tasks = ",".join(ts) if isinstance(ts, list) else str(ts or "")
        if not args.input_path:
            args.input_path = cfg.get("input_path") or cfg.get("input")
        if not args.output:
            args.output = cfg.get("output_path") or cfg.get("output")
        if not args.url:
            args.url = cfg.get("url")

    # 無 tasks 視為 no-op，但仍回傳 0
    run_pipeline(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
