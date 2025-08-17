from __future__ import annotations

# src/trainers/train_bert_spam_classifier.py
import argparse
import json
import os
from datetime import datetime

from datasets import Dataset
from sklearn.utils import shuffle
from transformers import BertForSequenceClassification, BertTokenizer, Trainer, TrainingArguments

LABEL2ID = {"ham": 0, "spam": 1}
ID2LABEL = {0: "ham", 1: "spam"}


def load_data(path):
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    data, stats = [], {}
    for item in raw:
        subject = item.get("subject", "")
        content = item.get("content", "")
        label = item.get("label")
        if label not in LABEL2ID:
            continue
        data.append({"text": subject.strip() + "\n" + content.strip(), "label": LABEL2ID[label]})
        stats[label] = stats.get(label, 0) + 1
    print(" 資料分布：", stats)
    return shuffle(data, random_state=42)


def tokenize(example, tokenizer):
    return tokenizer(
        example["text"],
        padding="max_length",
        truncation=True,
        max_length=512,
    )


def get_output_dir():
    now = datetime.now().strftime("%Y%m%d-%H%M")
    path = f"model/bert_spam_classifier_{now}"
    os.makedirs(path, exist_ok=True)
    return path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="訓練資料 JSON 路徑")
    parser.add_argument("--model", default="bert-base-chinese", help="預訓練模型")
    parser.add_argument("--epochs", type=int, default=5)
    args = parser.parse_args()

    print("[INFO] 載入資料...")
    dataset = Dataset.from_list(load_data(args.data))

    print("[INFO] 載入 tokenizer 和模型...")
    tokenizer = BertTokenizer.from_pretrained(args.model)
    tokenized = dataset.map(lambda x: tokenize(x, tokenizer), batched=True)

    model = BertForSequenceClassification.from_pretrained(
        args.model, num_labels=2, label2id=LABEL2ID, id2label=ID2LABEL
    )

    output_dir = get_output_dir()

    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=4,
        num_train_epochs=args.epochs,
        learning_rate=2e-5,
        weight_decay=0.01,
        save_strategy="epoch",
        save_total_limit=1,
        logging_steps=20,
        report_to="none",
    )

    print("[INFO] 開始訓練...")
    trainer = Trainer(model=model, tokenizer=tokenizer, args=training_args, train_dataset=tokenized)

    trainer.train()

    print(f"[INFO] 模型儲存到：{output_dir}")
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)


if __name__ == "__main__":
    main()
