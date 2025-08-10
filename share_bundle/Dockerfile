# Dockerfile（標準主流程 + 模型封裝版）

FROM python:3.10-slim

WORKDIR /app

# 安裝必要系統套件
RUN apt-get update && apt-get install -y \
    curl git build-essential \
    libglib2.0-0 libsm6 libxrender1 libxext6 \
    && apt-get clean

# 複製專案
COPY . /app

# 安裝 Python 套件
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 預設執行為 run_main.py（整合三層過濾 + 六分類）
CMD ["python", "cli/run_main.py", \
     "--spam_model", "model/bert_spam_classifier", \
     "--intent_model", "model/roberta-zh-checkpoint", \
     "--input", "data/testdata/email001.json", \
     "--output", "data/output/final.json"]
