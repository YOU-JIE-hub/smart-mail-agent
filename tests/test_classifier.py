# 檔案位置：tests/test_classifier.py
# 模組用途：單元測試 classifier.py，mock pipeline 測試分類與 fallback 機制

from classifier import IntentClassifier


def mock_pipeline_high_confidence(text, truncation=True):
    return [{"label": "詢問流程或規則", "score": 0.95}]


def mock_pipeline_low_confidence(text, truncation=True):
    return [{"label": "詢問流程或規則", "score": 0.2}]


def mock_pipeline_quote(text, truncation=True):
    return [{"label": "詢問流程或規則", "score": 0.9}]


def test_classifier_inference_with_high_confidence():
    clf = IntentClassifier(
        model_path="dummy", pipeline_override=mock_pipeline_high_confidence
    )
    result = clf.classify(
        "我要辦理退款流程", "想請問申請退費的具體流程"
    )  # 避開 fallback 條件
    assert result["predicted_label"] == "詢問流程或規則"
    assert result["confidence"] == 0.95


def test_classifier_inference_with_low_confidence_trigger_fallback():
    clf = IntentClassifier(
        model_path="dummy", pipeline_override=mock_pipeline_low_confidence
    )
    result = clf.classify("Hi", "Hello")  # fallback: is_generic + low confidence
    assert result["predicted_label"] == "其他"
    assert result["confidence"] == 0.2


def test_output_file_format():
    clf = IntentClassifier(model_path="dummy", pipeline_override=mock_pipeline_quote)
    result = clf.classify("合作洽詢", "我們有一項新的採購需求，想詢問方案與價格")
    assert isinstance(result, dict)
    assert "predicted_label" in result
    assert "confidence" in result
    assert result["predicted_label"] == "業務接洽或報價"  # 因命中 RE_QUOTE fallback
