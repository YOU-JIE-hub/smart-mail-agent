# Architecture


smart_mail_agent/
actions/ # 動作處理（sales, complaint, ...)
spam/ # 垃圾郵件管線（rule + ml + llm）
cli/ # CLI 入口（sma / sma-run / sma-spamcheck）
utils/ # 共用工具（logger, pdf, env, ...)

- 舊路徑 `src/spam/*` 有 compat shim → 轉發到 `smart_mail_agent.spam.*`
- 測試仍支援 `src.*` 引用（`PYTHONPATH=.` + shim）
