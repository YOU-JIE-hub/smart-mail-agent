#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape


def _candidate_dirs() -> list[str]:
    # src/utils/templater.py -> parents[2] 才是 repo 根目錄
    root = Path(__file__).resolve().parents[2]
    env_dir = os.getenv("SMA_TEMPLATES_DIR")
    dirs = []
    if env_dir:
        p = Path(env_dir)
        if not p.is_absolute():
            p = root / env_dir
        dirs.append(str(p))
    # repo 根目錄下的 templates/
    dirs.append(str(root / "templates"))
    # 兼容：src/templates/（若專案另放）
    dirs.append(str(root / "src" / "templates"))
    # 去重
    seen, out = set(), []
    for d in dirs:
        if d not in seen:
            seen.add(d)
            out.append(d)
    return out


def get_env() -> Environment:
    return Environment(loader=FileSystemLoader(_candidate_dirs()), autoescape=select_autoescape())


def render(template_name: str, context: Dict[str, Any]) -> str:
    return get_env().get_template(template_name).render(**context)
