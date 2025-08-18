#!/usr/bin/env python3
# 檔案位置: src/ai_rpa/scraper.py
# 模組用途: 網頁擷取與解析（requests + BeautifulSoup）
from __future__ import annotations
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
from ai_rpa.utils.logger import get_logger
log = get_logger("SCRAPER")

def scrape(url: str, timeout: int = 10) -> List[Dict]:
    """
    擷取單一 URL，回傳簡單結構化結果（標題與所有 <h1>/<h2> 文本）。
    參數:
        url: 目標網址
        timeout: 逾時秒數
    回傳:
        [{"tag": "h1"|"h2", "text": "..."}]
    """
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out: List[Dict] = []
    for tag in soup.find_all(["h1", "h2"]):
        txt = tag.get_text(strip=True)
        if txt:
            out.append({"tag": tag.name, "text": txt})
    log.info("抓取完成: %s, 標題數=%d", url, len(out))
    return out
