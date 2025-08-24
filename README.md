Smart Mail Agent — AI + RPA 整合專案

Ubuntu 22.04 · Python 3.10 · OCR + Scrape + NLP + LLM · 可執行 CLI · 可排程 · 專業 GitHub 展示

[功能]
  - OCR：Tesseract（eng/osd/chi-tra/chi-sim），支援圖片與 PDF
  - Scrape：requests + bs4 -> 乾淨文字
  - NLP：關鍵詞/規則分析
  - LLM：OpenAI 1.x；未設 OPENAI_API_KEY 時自動退化為本地摘要
  - Actions：輸出 JSON（或 PDF/TXT）
  - CLI：ai-rpa 一鍵執行；另有 sma-spamcheck, sma-run
  - 工程：pyproject.toml、ruff/black/isort、pytest、pre-commit、GitHub Actions

[快速開始]
    # 建議把這段加到 ~/.bashrc
    sma() { cd "$HOME/projects/smart-mail-agent" || return 2; export VIRTUAL_ENV_DISABLE_PROMPT=0; . "$HOME/.venv/sma/bin/activate"; PS1="(sma) $PS1"; }

    # 初始化
    sma
    pip install -e ".[ocr,llm,dev]"
    ai-rpa --input-path samples/nlp_demo.txt --tasks nlp,actions --output data/output/report.json

[OCR（中文）]
    ai-rpa --input-path samples/ocr_tra.png --tasks ocr,nlp,actions --output data/output/ocr_report.json

[LLM（可選）]
    echo "OPENAI_API_KEY=sk-..." > .env
    export OPENAI_API_KEY=sk-...
    ai-rpa --input-path samples/nlp_demo.txt --tasks nlp,actions --output data/output/report.json

[測試與格式]
    make lint
    make test

[結構]
    src/
      ai_rpa/                (OCR/Scrape/NLP/LLM/Actions 統一入口)
      smart_mail_agent/      (既有模組：ingestion/features/spam/…)
    tests_smoke/             (最小煙囪測試)
    assets/fonts/            (NotoSansTC-Regular.ttf)
    samples/                 (OCR/NLP 範例)
    data/output/             (產物)

授權：MIT License
