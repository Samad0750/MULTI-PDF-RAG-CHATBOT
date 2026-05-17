FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_HOST=0.0.0.0 \
    BACKEND_HOST=127.0.0.1 \
    BACKEND_PORT=8000 \
    BACKEND_URL=http://127.0.0.1:8000/api

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

RUN mkdir -p data/raw data/vectordb multi_pdf_rag/data/raw multi_pdf_rag/data/vectordb

EXPOSE 8501

CMD ["python", "-m", "multi_pdf_rag.app.run"]
