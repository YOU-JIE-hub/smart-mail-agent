import types, sys, importlib

def test_shim_delegates_to_impl(monkeypatch, tmp_path):
    sma = types.ModuleType("smart_mail_agent")
    ingestion = types.ModuleType("smart_mail_agent.ingestion")
    integrations = types.ModuleType("smart_mail_agent.ingestion.integrations")
    swa = types.ModuleType("smart_mail_agent.ingestion.integrations.send_with_attachment")

    calls = []
    def _impl(to, subject, body, file):
        calls.append((to, subject, body, file))
        return {"ok": True, "to": to, "file": file}

    swa.send_email_with_attachment = _impl
    integrations.send_with_attachment = swa

    monkeypatch.setitem(sys.modules, "smart_mail_agent", sma)
    monkeypatch.setitem(sys.modules, "smart_mail_agent.ingestion", ingestion)
    monkeypatch.setitem(sys.modules, "smart_mail_agent.ingestion.integrations", integrations)
    monkeypatch.setitem(sys.modules, "smart_mail_agent.ingestion.integrations.send_with_attachment", swa)

    shim = importlib.import_module("send_with_attachment")
    out = shim.send_email_with_attachment("x@y", "s", "b", str(tmp_path/"f.txt"))
    assert out["ok"] is True
    assert calls and calls[0][0] == "x@y"
