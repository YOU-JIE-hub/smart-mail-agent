.PHONY: help ensure-venv install format lint test-offline-venv fix-classifier fix-quotation clean-light clean-heavy

help:
	@echo "make ensure-venv          - 建 venv（如無）並升級 pip"
	@echo "make install              - 安裝開發套件"
	@echo "make format               - isort + black"
	@echo "make lint                 - flake8（需全過）"
	@echo "make test-offline-venv    - 自動啟 venv + OFFLINE 測試"
	@echo "make fix-classifier       - 修 transformers.from_pretrained 參數順序"
	@echo "make fix-quotation        - 修 quotation（專業優先、dict 回傳、PDF fallback）"
	@echo "make clean-light          - 清 cache/覆蓋/輸出"
	@echo "make clean-heavy          - 連 pip/hf 快取一起清"

ensure-venv:
	@test -d .venv || python -m venv .venv
	@. .venv/bin/activate; pip -q install -U pip

install: ensure-venv
	@. .venv/bin/activate; \
		pip install -r requirements.txt || true; \
		pip install -U pytest black isort flake8 python-dotenv

format:
	@. .venv/bin/activate; python -m isort .; python -m black .

lint:
	@. .venv/bin/activate; python -m flake8

test-offline-venv: ensure-venv
	@. .venv/bin/activate; OFFLINE=1 PYTHONPATH=src pytest -q -k "not online"

fix-classifier: ensure-venv
	@. .venv/bin/activate; \
		python tools/fix_from_pretrained_order_v3.py; \
		PYTHONPATH=src pytest -q -k "not online"

fix-quotation: ensure-venv
	@. .venv/bin/activate; \
		PYTHONPATH=src python - <<'PY' && \
		PYTHONPATH=src pytest -q -k "not online"
from pathlib import Path
code = r"""#!/usr/bin/env python3
from __future__ import annotations
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
PKG_BASIC="基礎"; PKG_PRO="專業"; PKG_ENT="企業"
KW_PRO=("自動化","排程","自動分類","專業")
KW_ENT=("整合","API","ERP","LINE","企業","功能")
DEFAULT_FONT_PATH=os.getenv("FONT_TTF_PATH","assets/fonts/NotoSansTC-Regular.ttf")
DEFAULT_OUT_DIR=Path("data/output")
def choose_package(subject:str, content:str)->Dict[str,object]:
    t=f"{subject or ''} {content or ''}".lower()
    if any(k.lower() in t for k in KW_PRO): pkg=PKG_PRO
    elif any(k.lower() in t for k in KW_ENT): pkg=PKG_ENT
    else: pkg=PKG_BASIC
    return {"package":pkg,"needs_manual":(pkg==PKG_BASIC)}
def _render_pdf(path:Path,title:str,lines:List[str])->str:
    from reportlab.pdfgen import canvas  # type: ignore
    from reportlab.lib.pagesizes import A4  # type: ignore
    font="Helvetica"
    try:
        from reportlab.pdfbase import pdfmetrics  # type: ignore
        from reportlab.pdfbase.ttfonts import TTFont  # type: ignore
        if Path(DEFAULT_FONT_PATH).exists():
            pdfmetrics.registerFont(TTFont("CJK", DEFAULT_FONT_PATH)); font="CJK"
    except Exception: pass
    path.parent.mkdir(parents=True, exist_ok=True)
    c=canvas.Canvas(str(path), pagesize=A4); w,h=A4; y=h-72
    c.setFont(font,16); c.drawString(72,y,title); y-=24
    c.setFont(font,12)
    for line in lines:
        c.drawString(72,y,line); y-=18
        if y<72: c.showPage(); c.setFont(font,12); y=h-72
    c.save(); return str(path)
def generate_pdf_quote(out_dir:Optional[os.PathLike|str]=None,*,package:Optional[str]=None,client_name:Optional[str]=None)->str:
    base=Path(out_dir) if out_dir is not None else DEFAULT_OUT_DIR
    base.mkdir(parents=True, exist_ok=True)
    pkg=package or PKG_BASIC; client=client_name or "client@example.com"
    ts=datetime.now().strftime("%Y%m%d-%H%M%S")
    pdf=base/f"quote-{pkg}-{ts}.pdf"
    title=f"Smart Mail Agent 報價 - {pkg}"
    lines=[f"客戶：{client}",f"方案：{pkg}",f"日期：{ts}","", "內容：此為測試用離線報價單（自動化產出）。"]
    try: return _render_pdf(pdf,title,lines)
    except Exception:
        txt=pdf.with_suffix(".txt"); txt.write_text(title+"\n"+"\n".join(lines), encoding="utf-8"); return str(txt)
__all__=["choose_package","generate_pdf_quote","PKG_BASIC","PKG_PRO","PKG_ENT"]
"""
Path("src/modules/quotation.py").write_text(code, encoding="utf-8")
print("wrote src/modules/quotation.py")
PY

clean-light:
	rm -rf .pytest_cache **/__pycache__ htmlcov .coverage* coverage.xml logs/* data/output/* || true

clean-heavy: clean-light
	python -m pip cache purge || true
	rm -rf ~/.cache/pip ~/.cache/huggingface ~/.cache/torch || true
