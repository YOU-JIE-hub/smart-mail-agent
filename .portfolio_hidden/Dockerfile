FROM python:3.11-slim
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONUNBUFFERED=1 TZ=Asia/Taipei
WORKDIR /app
COPY . /app
RUN python -m pip install -U pip && \
    if [ -f requirements.txt ]; then python -m pip install -e . -r requirements.txt; else python -m pip install -e .; fi
CMD ["python","-m","smart_mail_agent","--help"]
