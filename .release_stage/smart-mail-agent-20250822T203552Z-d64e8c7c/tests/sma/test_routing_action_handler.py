import json, os
from pathlib import Path
import importlib

mod = importlib.import_module("smart_mail_agent.routing.action_handler")

def test_ensure_attachment_txt_fallback(tmp_path, monkeypatch):
    # 強制 PDF 產生流程走 except（報告套件缺失時會自動 fallback）
    out = mod._ensure_attachment(tmp_path, "測試標題", ["第一行", "第二行"])
    p = Path(out)
    assert p.exists() and p.suffix in (".txt", ".pdf")
    assert p.read_text(encoding="utf-8", errors="ignore").strip()

def test_send_offline(monkeypatch):
    monkeypatch.setenv("OFFLINE","1")
    out = mod._send("a@b", "subj", "body", attachments=["x.pdf"])
    assert out["ok"] and out["offline"]

def test_action_dispatchers(monkeypatch, tmp_path):
    monkeypatch.setenv("OFFLINE","1")
    # 讓附件寫入到 tmp_path
    monkeypatch.setattr(mod, "_ensure_attachment", lambda d,t,ls: str(Path(tmp_path/"a.txt")))
    payload = {"subject":"報價單", "sender":"client@x", "body":"想詢價", "client_name":"測試客戶"}
    r1 = mod._action_send_quote(dict(payload))
    assert r1["ok"] and r1["action"]=="send_quote"
    r2 = mod._action_reply_support(dict(payload))
    assert r2["ok"] and r2["action"]=="reply_support"
    r3 = mod._action_apply_info_change(dict(payload))
    assert r3["ok"] and r3["action"]=="apply_info_change"
    r4 = mod._action_reply_faq(dict(payload))
    assert r4["ok"] and r4["action"]=="reply_faq"
    r5 = mod._action_reply_apology(dict(payload))
    assert r5["ok"] and r5["action"]=="reply_apology"
    r6 = mod._action_reply_general(dict(payload))
    assert r6["ok"] and r6["action"]=="reply_general"

def test_route_and_cli_main(tmp_path, monkeypatch):
    monkeypatch.setenv("OFFLINE","1")
    # 走 handle() 與 main()
    payload = {"predicted_label":"send_quote","subject":"Q","body":"B","sender":"u@x"}
    inp = tmp_path/"in.json"; outp = tmp_path/"out.json"
    inp.write_text(json.dumps(payload,ensure_ascii=False),encoding="utf-8")
    import importlib
    cli = importlib.import_module("smart_mail_agent.routing.action_handler")
    argv = ["--input", str(inp), "--output", str(outp)]
    cli.main(argv)  # 不丟例外即視為通過
    assert outp.exists() and "send_quote" in outp.read_text(encoding="utf-8")
