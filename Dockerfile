FROM python:3.11-slim as builder

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    python3 -c "import tomllib; f=open('pyproject.toml','rb'); d=tomllib.load(f); deps=d['project']['dependencies']; print('\n'.join(deps))" > /tmp/requirements.txt && \
    pip install -r /tmp/requirements.txt

COPY src/ ./src/
RUN pip install --no-cache-dir --no-deps -e .

FROM python:3.11-slim

RUN groupadd -r appuser && useradd -r -g appuser appuser

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN mkdir -p /app/assets /app/logs
WORKDIR /app

COPY src/ ./src/
RUN chown -R appuser:appuser /app && chmod -R 755 /app/logs
USER appuser

WORKDIR /app/src

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-", "--chdir", "/app/src"]
