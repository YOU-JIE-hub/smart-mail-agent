架構與資料流
    [Input: file/url] --> [OCR] --> [Scrape] --> [NLP] --> [LLM Summarize] --> [Actions(JSON/PDF/TXT)]
                                   ^                                     |
                                   '------------- 合併文字 --------------'

入口：ai-rpa --input-path <path|url> --tasks ocr,scrape,nlp,actions --output data/output/report.json
容錯：OCR 可回傳 str/dict/list；LLM 無金鑰時退化摘要
日誌：SMA_LOG_DIR=logs，輪替檔 logs/ai_rpa.log
