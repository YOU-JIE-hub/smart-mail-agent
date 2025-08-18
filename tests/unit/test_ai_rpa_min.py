from ai_rpa.file_classifier import classify_dir
from ai_rpa.nlp import analyze_text

def test_classify_dir_empty(tmp_path):
    out = classify_dir(str(tmp_path))
    assert out == {"image": [], "pdf": [], "text": [], "other": []}

def test_nlp_offline_keywords():
    res = analyze_text(["我想申請退款", "合作報價請提供"])
    assert set(res["labels"]) <= {"refund", "sales", "complaint", "other"}
