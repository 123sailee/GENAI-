FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY ui ./ui
COPY data ./data

RUN python -c "from app.vectorstore import store_embeddings; store_embeddings()"

EXPOSE 8000 8501

CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
