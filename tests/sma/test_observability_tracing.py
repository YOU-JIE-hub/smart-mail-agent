import importlib, uuid
tr = importlib.import_module("smart_mail_agent.observability.tracing")
def test_tracing_funcs():
    uid = tr.uuid_str(); assert uuid.UUID(uid)
    now = tr.now_ms(); assert isinstance(now,int) and now>0
    assert tr.elapsed_ms(now-5) >= 0
    assert tr.elapsed_ms("bad") == 0
