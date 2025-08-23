#!/usr/bin/env python3
# 檔案位置: src/ai_rpa/main.py
# 模組用途: Orchestrator/CLI，與 PDF 設計相符
from __future__ import annotations
import argparse
from typing import List, Dict, Any
from ai_rpa.utils.config_loader import load_config
from ai_rpa.utils.logger import get_logger
from ai_rpa.ocr import run_ocr
from ai_rpa.scraper import scrape
from ai_rpa.file_classifier import classify_dir
from ai_rpa.nlp import analyze_text
from ai_rpa.actions import write_json

log = get_logger("CLI")

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="AI+RPA pipeline")
    p.add_argument("--config", default="configs/ai_rpa_config.yaml")
    p.add_argument("--tasks", default="", help="逗號分隔: ocr,scrape,classify_files,nlp,actions")
    p.add_argument("--input-path", default="data/input")
    p.add_argument("--url", default="https://example.com")
    p.add_argument("--output", default="data/output/report.json")
    p.add_argument("--log-level", default="INFO")
    p.add_argument("--dry-run", action="store_true")
    return p.parse_args()

def main() -> int:
    args = parse_args()
    cfg = load_config(args.config if args.config else None)
    tasks = [t for t in (args.tasks.split(",") if args.tasks else cfg.get("tasks", [])) if t]
    out: Dict[str, Any] = {"steps": [], "errors": []}

    # 1) OCR
    if "ocr" in tasks:
        ocr_in = f"{args.input_path}/sample.jpg"
        try:
            res = run_ocr(ocr_in)
            out["steps"].append({"ocr": res})
        except Exception as e:
            out["errors"].append({"ocr": str(e)})

    # 2) Scrape
    if "scrape" in tasks:
        try:
            out["steps"].append({"scrape": scrape(args.url)})
        except Exception as e:
            out["errors"].append({"scrape": str(e)})

    # 3) File classify
    if "classify_files" in tasks:
        try:
            out["steps"].append({"classify_files": classify_dir(args.input_path)})
        except Exception as e:
            out["errors"].append({"classify_files": str(e)})

    # 4) NLP
    if "nlp" in tasks:
        texts: List[str] = []
        for step in out["steps"]:
            if "ocr" in step and step["ocr"].get("text"):
                texts.append(step["ocr"]["text"])
            if "scrape" in step:
                texts.extend([x["text"] for x in step["scrape"]])
        try:
            out["steps"].append({"nlp": analyze_text(texts, cfg.get("nlp", {}).get("model", "offline-keyword"))})
        except Exception as e:
            out["errors"].append({"nlp": str(e)})

    # 5) Actions
    if "actions" in tasks and not args.dry_run:
        write_json(out, args.output)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
