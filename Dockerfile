FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    USE_LIGHTWEIGHT_RETRIEVAL=true

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY ui ./ui
COPY data ./data
COPY prompts ./prompts

EXPOSE 8000 8501

CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
