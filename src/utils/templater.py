# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"
_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=select_autoescape(["html", "xml"])
)


def render(name: str, **kw) -> str:
    tmpl = _env.get_template(name)
    return tmpl.render(**kw)
