FROM python:3.11-slim

WORKDIR /app

# Install system dependencies & FFmpeg for worker media processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    ffmpeg \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml .
COPY packages/ packages/
COPY services/worker/ services/worker/

ENV PYTHONPATH=/app

CMD ["python", "services/worker/main.py"]
