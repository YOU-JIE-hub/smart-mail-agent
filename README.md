# Smart Mail Agent（面試展示版）
狀態徽章：見 GitHub Actions CI

快速開始（步驟）：
1. 建立 venv 與安裝依賴（requirements.txt、requirements-dev.txt）
2. 執行 `make demo-all` 產生範例輸出
3. 執行 `make show-summary` 檢視摘要
4. 離線 E2E：`OFFLINE=1 PYTHONPATH=src pytest -q tests/e2e`

策略亮點：
- 投訴 P1 自動 CC + SLA，輸出保證含 meta.next_step
- `--dry-run`：頂層與 meta 同步 dry_run=true
- JSONL 日誌永不拋例外；輸出含 logged_path

中文 PDF 字型（可選）：
- FONT_PATH=assets/fonts/NotoSansTC-Regular.ttf
- PDF_FONT_FALLBACK=1
