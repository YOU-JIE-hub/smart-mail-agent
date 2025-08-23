import json, os, subprocess, sys, tempfile, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
PYEXE = sys.executable
ENV = os.environ.copy()
ENV["PYTHONPATH"] = str(ROOT)

def _run(json_obj, *extra):
    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", suffix=".json", delete=False) as f:
        json.dump(json_obj, f, ensure_ascii=False); f.flush()
        out = subprocess.check_output([PYEXE, "-m", "src.run_action_handler", "--json", f.name, *extra], env=ENV, text=True)
    return json.loads(out)

def test_baseline_not_whitelisted():
    o = _run({"subject":"一般詢問","from":"a@other.example","predicted_label":"reply_faq","attachments":[]})
    assert o["action_name"] == "reply_faq"
    assert o["meta"]["whitelisted"] is False
    assert o["meta"]["priority"] == "P3"
    assert o["meta"]["SLA_eta"] == "24h"
    assert o["meta"]["next_step"].endswith("normal_queue")
    assert o["subject"].startswith("[自動回覆] ")

def test_positional_and_flag_whitelist():
    j = {"subject":"一般詢問","from":"a@other.example","predicted_label":"reply_faq","attachments":[]}
    o1 = _run(j, "whitelist")
    o2 = _run(j, "--whitelist")
    assert o1["meta"]["whitelisted"] is True
    assert o2["meta"]["whitelisted"] is True

def test_domain_whitelist_and_env():
    j = {"subject":"x","from":"u@trusted.example","predicted_label":"reply_faq","attachments":[]}
    o = _run(j)
    assert o["meta"]["whitelisted"] is True
    j2 = {"subject":"x","from":"u@other.example","predicted_label":"reply_faq","attachments":[]}
    env = ENV.copy(); env["SMA_FORCE_WHITELIST"]="1"
    with tempfile.NamedTemporaryFile("w+", encoding="utf-8", suffix=".json", delete=False) as f:
        json.dump(j2, f, ensure_ascii=False); f.flush()
        out = subprocess.check_output([PYEXE, "-m", "src.run_action_handler", "--json", f.name], env=env, text=True)
    o2 = json.loads(out)
    assert o2["meta"]["whitelisted"] is True

def test_risky_attachment_and_complaint_priority_and_output_file(tmp_path):
    j = {"subject":"urgent 請處理","from":"u@other.example","predicted_label":"complaint",
         "attachments":[{"filename":"evil.exe","size":123}]}
    in_path = tmp_path/"in.json"; in_path.write_text(json.dumps(j, ensure_ascii=False), encoding="utf-8")
    out_path = tmp_path/"result.json"
    out = subprocess.check_output(
        [PYEXE, "-m", "src.run_action_handler", "--json", str(in_path), "--output", str(out_path), "--simulate-failure", "network"],
        env=ENV, text=True
    )
    data = json.loads(out)
    assert data["meta"]["priority"] == "P2"
    assert data["meta"]["SLA_eta"] == "8h"
    assert data["simulate_failure"] is True
    assert data["simulate_type"] == "network"
    saved = json.loads(out_path.read_text(encoding="utf-8"))
    assert saved["subject"].startswith("[已收件] ")
