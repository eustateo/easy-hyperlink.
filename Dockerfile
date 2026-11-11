FROM ghcr.io/astral-sh/uv:0.12.1 AS uv
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1
WORKDIR /app
COPY --from=uv /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev --no-editable
COPY api.py manage.py ./
COPY config ./config
COPY templates ./templates
COPY static ./static

USER 10001:10001
EXPOSE 8000
CMD ["/app/.venv/bin/uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--no-proxy-headers", "--no-server-header", "--limit-concurrency", "40", "--timeout-keep-alive", "5"]
