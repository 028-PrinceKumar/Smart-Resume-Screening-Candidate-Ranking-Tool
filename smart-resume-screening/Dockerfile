# Multi-purpose Dockerfile - the target service (api or streamlit) is chosen
# via the CMD override in docker-compose.yml.
FROM python:3.11-slim

WORKDIR /app

# System dependencies for PDF parsing.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

EXPOSE 8000 8501

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
