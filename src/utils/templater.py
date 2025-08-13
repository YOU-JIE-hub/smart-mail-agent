# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

_THIS = Path(__file__).resolve()
SRC_DIR = _THIS.parents[1]  # .../src
ROOT_DIR = SRC_DIR.parent  # repo root
SEARCH = [ROOT_DIR / "templates", SRC_DIR / "templates"]

_env = Environment(
    loader=FileSystemLoader([str(p) for p in SEARCH]), autoescape=select_autoescape(["html", "xml"])
)


def render(name: str, **kw) -> str:
    tmpl = _env.get_template(name)
    return tmpl.render(**kw)
