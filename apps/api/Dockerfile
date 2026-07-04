ARG PYTHON_VERSION=3.12-slim

# ── Base ──────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION} AS base
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    tesseract-ocr \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Development ───────────────────────────────────────────────
FROM base AS development
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"
COPY . .
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ── Production ────────────────────────────────────────────────
FROM base AS production
COPY pyproject.toml .
RUN pip install --no-cache-dir -e "." && pip cache purge
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .

RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
