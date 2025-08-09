# scripts/gen_all_testdata.py
# 產生 Smart-Mail-Agent 專案所有正式測試資料（分類 / spam / pipeline / 錯誤）

import json
import os

# 各分類輸出路徑
paths = {
    "classifier": "data/testdata/classifier",
    "spam": "data/testdata/spam",
    "pipeline": "data/testdata/pipeline",
}

for path in paths.values():
    os.makedirs(path, exist_ok=True)

# 分類測資（六分類）
classifier_samples = [
    {
        "filename": "ham_tech_support_01.json",
        "path": paths["classifier"],
        "data": {
            "subject": "APP 出現錯誤訊息",
            "body": "打開應用程式後一直出現錯誤，請問怎麼處理？",
            "expected_label": "請求技術支援",
        },
    },
    {
        "filename": "ham_info_change_01.json",
        "path": paths["classifier"],
        "data": {
            "subject": "我要變更公司地址",
            "body": "您好，請幫我把聯絡地址改成台中市西屯區。",
            "expected_label": "申請修改資訊",
        },
    },
    {
        "filename": "ham_complaint_01.json",
        "path": paths["classifier"],
        "data": {
            "subject": "對你們服務不滿",
            "body": "我使用你們服務遇到很多問題，希望有人聯繫我解釋清楚。",
            "expected_label": "投訴與抱怨",
        },
    },
    {
        "filename": "ham_general_inquiry_01.json",
        "path": paths["classifier"],
        "data": {
            "subject": "請問如何取消訂閱？",
            "body": "我想了解取消訂閱的流程與時間限制。",
            "expected_label": "詢問流程或規則",
        },
    },
    {
        "filename": "ham_quotation_01.json",
        "path": paths["classifier"],
        "data": {
            "subject": "請提供企業報價",
            "body": "我們有意採購 10 套授權，請問企業授權方案有哪些？",
            "expected_label": "業務接洽或報價",
        },
    },
    {
        "filename": "ham_unknown_01.json",
        "path": paths["classifier"],
        "data": {
            "subject": "Hello there",
            "body": "Just testing your system. How are you doing?",
            "expected_label": "其他",
        },
    },
]

# spam 三層測資
spam_samples = [
    {
        "filename": "spam_rule.json",
        "path": paths["spam"],
        "data": {
            "subject": "限時免費裸聊",
            "body": "現在加入 LINE：abc123 立即體驗！",
            "expected_stage": "rule",
        },
    },
    {
        "filename": "spam_ml.json",
        "path": paths["spam"],
        "data": {
            "subject": "投資回報 10 倍保證",
            "body": "我們提供快速投資計畫，日賺萬元",
            "expected_stage": "ml",
        },
    },
    {
        "filename": "spam_llm.json",
        "path": paths["spam"],
        "data": {
            "subject": "帳號異常登入通知",
            "body": "我們偵測到來自陌生地點的登入。若不是您本人操作，請點此確認帳號安全：https://suspicious-link.com",
            "expected_stage": "llm",
        },
    },
    {
        "filename": "ham_legit.json",
        "path": paths["spam"],
        "data": {
            "subject": "付款方式有哪些？",
            "body": "我想了解可以刷卡還是轉帳，謝謝。",
            "expected_stage": "none",
        },
    },
]

# pipeline 測資（分類 + 自動處理 + 錯誤）
pipeline_samples = [
    {
        "filename": "quote_request.json",
        "path": paths["pipeline"],
        "data": {
            "subject": "我要企業報價方案",
            "body": "請問企業授權如何收費？我們有 50 人要使用。",
            "sender": "user@example.com",
            "expected_label": "業務接洽或報價",
        },
    },
    {
        "filename": "change_info.json",
        "path": paths["pipeline"],
        "data": {
            "subject": "我要改地址",
            "body": "請幫我把地址從高雄改成台北市信義區",
            "sender": "user@example.com",
            "expected_label": "申請修改資訊",
        },
    },
    {
        "filename": "error_missing_subject.json",
        "path": paths["pipeline"],
        "data": {"body": "請問我要修改地址怎麼做？", "sender": "user@example.com"},
    },
    {
        "filename": "error_no_model_path.json",
        "path": paths["pipeline"],
        "data": {
            "subject": "我要報價",
            "body": "請幫我報一個企業方案",
            "sender": "user@example.com",
        },
    },
    {
        "filename": "error_smtp_missing.json",
        "path": paths["pipeline"],
        "data": {
            "subject": "我要買企業授權",
            "body": "請幫我寄報價單，謝謝",
            "sender": "user@example.com",
        },
    },
]

# 合併所有測資
all_samples = classifier_samples + spam_samples + pipeline_samples

# 寫入檔案
for sample in all_samples:
    out_path = os.path.join(sample["path"], sample["filename"])
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(sample["data"], f, ensure_ascii=False, indent=2)

print(f"已成功產出 {len(all_samples)} 筆測資於資料夾：")
for k, v in paths.items():
    print(f"- {k}: {v}")
