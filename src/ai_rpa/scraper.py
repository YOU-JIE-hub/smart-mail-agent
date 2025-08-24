#!/usr/bin/env python3
# 檔案位置: src/ai_rpa/scraper.py
# 模組用途: 簡易網頁擷取（示範：抓取 h1/h2）
from __future__ import annotations

from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from ai_rpa.utils.logger import get_logger

log = get_logger("SCRAPER")


def scrape(url: str) -> List[Dict[str, str]]:
    """
    下載頁面並擷取 h1/h2 文本。
    回傳: [{"tag":"h1","text":"..."}, ...]
    """
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out: List[Dict[str, str]] = []
    for tag in soup.find_all(["h1", "h2"]):
        txt = tag.get_text(strip=True)
        if txt:
            out.append({"tag": tag.name, "text": txt})
    log.info("抓取完成: %s, 標題數=%d", url, len(out))
    return out
